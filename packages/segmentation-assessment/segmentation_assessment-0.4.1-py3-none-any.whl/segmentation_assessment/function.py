import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pandas as pd
from PIL import Image
import skimage as ski
import os
import cv2
import numpy as np
import rasterio.features
from rasterio.transform import Affine
from scipy import ndimage,stats
import json
from sklearn import metrics
import sys
# MinMax normalisation (values between O and 1)
def normalize(img):
  img=(img-np.min(img))/(np.max(img)-np.min(img))
  return img

# MinMax normalisation (values between O and 255)
def normalize_255(img):
  img=((img-np.min(img))/(np.max(img)-np.min(img)))*255
  return img

#Show borders of cells mask (from a dataframe) on a image
def outline(img,df,w=1,color=(255,255,255)):
    for i in df.index.to_list():
        img_outline=np.zeros((img.shape[0],img.shape[1]))
        list_pixel= df.loc[i,"coords"]
        for p in list_pixel:
            img_outline[p[0],p[1]]=1
        img_outline=np.uint8(img_outline)
        contours, hierarchy = cv2.findContours(img_outline, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(img, contours, -1, color, w)
    return img    

#Show borders of cells mask (from a dataframe) on a image
# The borders are red if the iou < threshold and blue if iou>threshold
# The border of manualy segmentated object are white 
# if c=0 the borders will be white 
def outline_iou(path_img,name,algo,df,threshold=0.5,c=0):
    if os.path.isdir("./segmentation_quality")==False:
        os.mkdir("./segmentation_quality")
    if os.path.isdir("./segmentation_quality/outline_iou")==False:
        os.mkdir("./segmentation_quality/outline_iou")
    if os.path.isdir("./segmentation_quality/outline_iou/"+algo)==False:
        os.mkdir("./segmentation_quality/outline_iou/"+algo)
    crop= np.array(Image.open(path_img))
    for i in df.index.to_list():
        img=np.zeros((crop.shape[0],crop.shape[1]))
        if c!=0:
            color=(255,255,255)
        elif df.loc[i,"iou"]>threshold:
            color=(0,0,255)
        else:
            color=(255,0,0)
        list_pixel= df.loc[i,"coords"]
        for p in list_pixel:
            img[p[0],p[1]]=1
        img=np.uint8(img)
        contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(crop, contours, -1, color, 1)
        cv2.imwrite("./segmentation_quality/outline_iou/"+algo+"/"+name[:-4]+".png",normalize_255(crop))
    return crop

# Create a dataframe with informations (coordinates,area...) for each object of the image 
# The object from the predicted mask are filtered (minimum and maximum size in the parameters)
def mask_to_df(path_mask,min_size=0,max_size=10000000):
    #img= np.array(Image.open(path_img))
    mask= np.array(Image.open(path_mask))
    label=ski.measure.label(mask,connectivity=mask.ndim)
    df_mask=ski.measure.regionprops_table(label,intensity_image=mask,properties=["area","coords","equivalent_diameter_area","bbox","axis_major_length","axis_minor_length","centroid"])
    df_mask=pd.DataFrame(df_mask)
    df=df_mask[df_mask.loc[:,"area"]>min_size].copy()
    df=df[df.loc[:,"area"]<max_size].copy()
    return df

#Show the borders of all the object of an image for all the folders
# Three markers can be choosen as parameters and will be on the image
def display_outline_mask(path_img,path_mask,marker,path="./"):
    #if os.path.isdir("./segmentation_quality")==False:
        #os.mkdir("./segmentation_quality")
    #path=path_file+"segmentation_quality/mask_outline_"+marker
    #if os.path.isdir(path)==False:
        #os.mkdir(path)
    for algo in os.listdir(path_mask):
        if os.path.isdir(path+"/"+algo)==False:
            os.mkdir(path+"/"+algo)
        for name_img in os.listdir(path_img):
            img_dna=plt.imread(path_img+"/"+name_img+"/DNA.png")
            img_outline=np.zeros((img_dna.shape[0],img_dna.shape[1],3))
            img_outline[:,:,2]=normalize_255(img_dna)
            if marker!="":
                img_outline[:,:,1]=normalize_255(plt.imread(path_img+"/"+name_img+"/"+marker+".png"))
            df_mask=mask_to_df(path_mask+"/"+algo+"/"+name_img+".tif")
            print(df_mask.shape)
            img_outline=outline(img_outline,df_mask)
            cv2.imwrite(path+"/"+algo+"/"+name_img+".png",normalize_255(img_outline))

# Create an image with the predicted mask in different colors and the outline of the ground truth
def outline_mask_color(path_img,path_mask,path_file,algo,min_size,max_size):
    if os.path.isdir(path_file+"outline_color")==False:
        os.mkdir(path_file+"outline_color")
    if os.path.isdir(path_file+"outline_color/"+algo)==False:
        os.mkdir(path_file+"outline_color/"+algo)
    
    for file_img,file_mask in zip(os.listdir(path_img),os.listdir(path_mask+"/"+algo)):
        img= np.array(Image.open(path_img+"/"+file_img))
        crop_iou=np.zeros((img.shape[0],img.shape[1],3))
        df_mask=mask_to_df(path_mask+"/"+algo+"/"+file_mask,min_size,max_size)
        df_truth=mask_to_df(path_mask+"/"+algo+"/"+file_mask)
        rgb_colors={}
        for name, hex in matplotlib.colors.cnames.items():
            rgb_colors[name] = matplotlib.colors.to_rgb(hex)
        for i in df_mask.index:
            color=list(rgb_colors.values())[np.random.randint(len(rgb_colors))]
            for p in df_mask.loc[i,"coords"]:
                crop_iou[p[0],p[1]]=color
        img=outline(normalize_255(crop_iou),df_truth)
        cv2.imwrite(path_file+"outline_color/"+algo+"/"+file_img[:-4]+".png",normalize_255(img))


#Calcul the mean iou between two masks
#return a dict with the pair of object (index from the dataframe predicted, and ground truth) and the iou in value
#return the two dataframe predicted and truth with a new column : iou 
def iou_mean(df_truth,df_mask):
  dico_objet={}
  list_iou=[]
  df_mask["iou"]=float(0)
  df_truth["iou"]=float(0)
  for i in df_mask.index.to_list():
    centre_mask=(df_mask.loc[i,"centroid-1"],df_mask.loc[i,"centroid-0"])
    diametre_mask=df_mask.loc[i,"equivalent_diameter_area"]+5
    list_cell_mask=[]
    for p in df_mask.loc[i,"coords"]:
          list_cell_mask.append(tuple(p))
    for j in df_truth.index.to_list():
     centre_truth=(df_truth.loc[j,"centroid-1"],df_truth.loc[j,"centroid-0"])
     diametre_truth=df_truth.loc[j,"equivalent_diameter_area"]+5
     distance=np.abs(centre_mask[0]-centre_truth[0])+np.abs(centre_mask[1]-centre_truth[1])
     if distance<diametre_mask/2 or distance<diametre_truth/2:
      list_cell_truth=[]
      for p in df_truth.loc[j,"coords"]:
          list_cell_truth.append(tuple(p))
      total_mask=len(list_cell_mask)
      total_truth=len(list_cell_truth)
      intersection= len(list(set(list_cell_truth).intersection(set(list_cell_mask))))
      if intersection>0:
          iou=intersection/(total_mask+total_truth-intersection)
          if iou>df_mask.loc[i,"iou"] and iou>df_truth.loc[j,"iou"]:
            list_iou.append(iou)
            df_mask.loc[i,"iou"]=iou
            df_truth.loc[j,"iou"]=iou
            dico_objet[(i,j)]=iou

  iou=np.around(np.sum(list_iou)/(df_truth.shape[0]+df_mask.shape[0]-len(list_iou)),2)
  return dico_objet,df_mask,df_truth,iou

#Apply the function to calcul iou
def calcul_iou(path_img,path_mask,path_truth,min_size=0,max_size=10000000):
    df_mask=mask_to_df(path_mask,min_size,max_size)
    df_truth=mask_to_df(path_truth)
    dico_objet,df_mask,df_truth,iou=iou_mean(df_truth,df_mask)
    return iou,dico_objet,df_mask,df_truth

# return recall,precision, nb of true positive, nb of false positive and nb of false negative
#if an object has an iou> threshold, it's considered as positive
def recall_precision(thresh,df_mask,df_truth):
    list_true_pos=[i for i in df_mask.loc[:,"iou"] if i>thresh]
    list_false_pos=[i for i in df_mask.loc[:,"iou"] if i<thresh]
    list_false_neg=[i for i in df_truth.loc[:,"iou"] if i<thresh]

    recall=np.around(len(list_true_pos)/df_truth.shape[0],2)
    precision=np.around(len(list_true_pos)/(len(list_true_pos)+len(list_false_pos)),2)
    
    return recall,precision,len(list_true_pos),len(list_false_pos),len(list_false_neg)

def distribution_number_object(path_img="./img",path_mask="./mask",path_file="./segmentation_quality/",dico_algo_min={},dico_algo_max={},title=""):
    plt.figure(figsize=(30,15))
    dico_algo_nb={}
    list_name_img=os.listdir(path_img)
    for algo in os.listdir(path_mask):
        dico_algo_nb[algo]=[]
        for file_mask in os.listdir(path_mask+"/"+algo):
            if dico_algo_max!={} and dico_algo_min!={} and algo!="truth":
                df=mask_to_df(path_mask+"/"+algo+"/"+file_mask,dico_algo_min[algo],dico_algo_max[algo])
            else:
                df=mask_to_df(path_mask+"/"+algo+"/"+file_mask)
            dico_algo_nb[algo].append(df.shape[0])
    width=0.8/(len(dico_algo_nb.keys()))
    for i,k in enumerate(dico_algo_nb.keys()):
        if i==0:
            x_axis=np.arange(len(list_name_img))
        else:
            x_axis=[x + width for x in x_axis] 
        plt.bar(x_axis,dico_algo_nb[k],label=k,width=width)
        
    plt.title("Number of objects",fontsize=35)
    plt.ylabel("Number of objects",fontsize=30)
    plt.xlabel("Images",fontsize=30)
    plt.xticks([r + width for r in range(len(list_name_img))],list_name_img,rotation=60)
    plt.legend(fontsize=20)
    #plt.text(3,np.max(list(dico_roi_ratio.values())),"Mean percentage= "+str(mean_ratio),fontsize=15)
    plt.savefig(path_file+title)
    #return mean_ratio,dico_roi_ratio


    plt.figure()
    y_label=[]
    x_label=[]
    for k in dico_algo_nb.keys():
        for roi in dico_algo_nb[k]:
            x_label.append(k)
            y_label.append(roi)
    sns.swarmplot(x=x_label,y=y_label,color="black")
    sns.boxplot(x=x_label,y=y_label,showmeans=True)
    plt.title("Average number of objects",fontsize=10)
    plt.ylabel("Number of objects",fontsize=10)
    plt.xlabel("Images",fontsize=15)
    plt.savefig(path_file+"mean_"+title)


#Make an histograme of the size of the object in the ground truth mask
def size_distribution(path_mask="./mask",path_file="./",dico_algo_min={},dico_algo_max={},title="size_distribution.png"):
    if os.path.isdir("./segmentation_quality")==False:
        os.mkdir("./segmentation_quality")
    dico_algo_size={}
    for algo in os.listdir(path_mask):
        dico_algo_size[algo]=[]
        for name_img in os.listdir(path_mask+"/"+algo):
            if dico_algo_max!={} and dico_algo_min!={} and algo!="truth":
                df_mask=mask_to_df(path_mask+"/"+algo+"/"+name_img,dico_algo_min[algo],dico_algo_max[algo])
            else:
                df_mask=mask_to_df(path_mask+"/"+algo+"/"+name_img)
            for a in df_mask["area"]:
                dico_algo_size[algo].append(a)
    """
    dico_algo_size_mean={}
    for algo in dico_algo_size.keys():
        dico_algo_size[algo]=np.mean(dico_algo_size[algo]) 
    """
    list_k=[]
    list_v=[]
    for k in dico_algo_size.keys():
        list_k.append(k)
        list_v.append(dico_algo_size[k])
    plt.figure(figsize=(20,12))
    plt.title("mask object size distribution",fontsize=35)
    plt.xlabel("number of object",fontsize=25)
    plt.ylabel("size in pixel",fontsize=25)
    for i in range(len(list_k)):
        sns.histplot(list_v[i],kde=True,label=list_k[i])

    #plt.hist(list_v,label=list_k,density=True)
    #plt.tight_layout()
    plt.legend(loc='upper right',fontsize=20)
    plt.savefig(path_file+title)

# returns the maximum size that must be filtered to obtain the best average iou
# make a plot of the mean iou according the maximum size in the predicted mask
def calcul_max_size(path_img,path_mask,path_file,step=0):
    dico_algo_size_iou={}
    for algo in os.listdir(path_mask):
        if algo!="truth":
            dico_algo_size_iou[algo]={}
            for file in os.listdir(path_mask+"/"+algo):
                df_truth=mask_to_df(path_mask+"/truth/"+file,0)
                df_mask=mask_to_df(path_mask+"/"+algo+"/"+file,0)
                if step==0:
                    step=np.max(df_mask["area"])//10
                for size in range(0,int(max(df_mask["area"])),int(step)):
                    if size not in dico_algo_size_iou.keys():
                        dico_algo_size_iou[algo][size]=[]
                    df=df_mask[df_mask.loc[:,"area"]<size].copy()
                    dico_objet,df,df_truth,iou=iou_mean(df_truth,df)
                    dico_algo_size_iou[algo][size].append(iou)
    dico_algo_mean={}
    for k in dico_algo_size_iou.keys():
        dico_algo_mean[k]=[]
        for k2 in dico_algo_size_iou[k].keys():
            dico_algo_mean[k].append(np.mean(dico_algo_size_iou[k][k2]))
    dico_algo_best={}
    for k in dico_algo_size_iou.keys():
        dico_algo_best[k]=list(dico_algo_size_iou[k].keys())[np.argmax(dico_algo_mean[k])]
    plt.figure()
    plt.title("IOU according to the maximum size of an object in the predicted mask")
    plt.ylim(0)
    plt.xlabel("Size (µm²)")
    plt.ylabel("IOU")
    for n,k in enumerate(dico_algo_size_iou.keys()):
        plt.plot(list(dico_algo_size_iou[k].keys()),dico_algo_mean[k],label=k)
        plt.text(0,0.95-(n/20),"Algo: "+k+" Best Iou: "+str(np.max(dico_algo_mean[k]))+" for a size of: "+str(list(dico_algo_size_iou[k].keys())[np.argmax(dico_algo_mean[k])])+" µm²")

    plt.legend(loc='upper right')
    plt.savefig(path_file+"IOU_max_size.png")
    return dico_algo_best

def calcul_min_size(path_img,path_mask,path_file,step=100):
    dico_algo_size_iou={}
    for algo in os.listdir(path_mask):
        if algo!="truth":
            dico_algo_size_iou[algo]={}
            for file in os.listdir(path_mask+"/"+algo):
                df_truth=mask_to_df(path_mask+"/truth/"+file,0)
                df_mask=mask_to_df(path_mask+"/"+algo+"/"+file,0)
                if step==0:
                    step=np.max(df_mask["area"])//10
                for size in range(0,int(max(df_truth["area"])//2),int(step)):
                    if size not in dico_algo_size_iou.keys():
                        dico_algo_size_iou[algo][size]=[]
                    df=df_mask[df_mask.loc[:,"area"]>size].copy()
                    dico_objet,df,df_truth,iou=iou_mean(df_truth,df)
                    dico_algo_size_iou[algo][size].append(iou)
    dico_algo_mean={}
    for k in dico_algo_size_iou.keys():
        dico_algo_mean[k]=[]
        for k2 in dico_algo_size_iou[k].keys():
            dico_algo_mean[k].append(np.mean(dico_algo_size_iou[k][k2]))
    dico_algo_best={}
    for k in dico_algo_size_iou.keys():
        dico_algo_best[k]=list(dico_algo_size_iou[k].keys())[np.argmax(dico_algo_mean[k])]
    plt.figure()
    plt.title("IOU according to the minimum size of an object in the predicted mask")
    plt.ylim(0)
    plt.xlabel("Size (µm²)")
    plt.ylabel("IOU")
    for n,k in enumerate(dico_algo_size_iou.keys()):
        plt.plot(list(dico_algo_size_iou[k].keys()),dico_algo_mean[k],label=k)
        plt.text(0.1,0.95-(n/20),"Algo: "+k+" Best Iou: "+str(np.max(dico_algo_mean[k]))+" for a size of: "+str(list(dico_algo_size_iou[k].keys())[np.argmax(dico_algo_mean[k])])+" µm²")
    plt.legend()
    plt.savefig(path_file+"IOU_min_size.png")
    return dico_algo_best

#calcul the auc
#make a plot of the precision according the IOU
def calcul_auc(path_img,path_mask,path_file,title,dict_min_size={},dict_max_size={}):
    dico_iou={}
    list_thresh=np.arange(0,1,0.1)
    plt.figure(figsize=(20,12))
    plt.title("Average precision",fontsize=40)
    dico_algo_ap={}
    for n,algo in enumerate(os.listdir(path_mask)):
        if algo !="truth":
            if algo not in dict_max_size.keys():
                dict_max_size[algo]=100000000
            if algo not in dict_min_size.keys():
                dict_min_size[algo]=0
            dico_iou[algo]={}
            for thresh in list_thresh:
                t=str(thresh)
                dico_iou[algo][t]={}
                dico_iou[algo][t]["precision"]=[]
                dico_iou[algo][t]["recall"]=[]
                dico_iou[algo][t]["true_pos"]=[]
                dico_iou[algo][t]["false_pos"]=[]
                dico_iou[algo][t]["false_neg"]=[]

                for file_img,file_mask in zip(os.listdir(path_img),os.listdir(path_mask+"/"+algo)):
                    iou,dico_objet,df_mask,df_truth=calcul_iou(path_img+"/"+file_img,path_mask+"/"+algo+"/"+file_mask,path_mask+"/truth/"+file_mask,dict_min_size[algo],dict_max_size[algo])
                    recall,precision,true_pos,false_pos,false_neg=recall_precision(thresh,df_mask,df_truth)
                    dico_iou[algo][t]["precision"].append(precision)
                    dico_iou[algo][t]["recall"].append(recall)
                    dico_iou[algo][t]["true_pos"].append(true_pos)
                    dico_iou[algo][t]["false_pos"].append(false_pos)
                    dico_iou[algo][t]["false_neg"].append(false_neg)

            #list_true_pos_rate.append(true_pos/(true_pos+false_neg))
            #list_false_pos_rate.append(false_pos/(true_neg+false_pos))
            list_recall=[np.mean(dico_iou[algo][k]["recall"]) for k in dico_iou[algo].keys()]
            list_precision=[np.mean(dico_iou[algo][k]["precision"]) for k in dico_iou[algo].keys()]

            list_precision=np.array(list_precision)
            list_recall=np.array(list_recall)
            #AP = np.around(np.sum((list_thresh[:-1] - list_thresh[1:]) * list_precision[:-1]),2)
            AP=np.around(metrics.auc(list_thresh,list_precision),2)
            dico_algo_ap[algo]=np.around(AP,2)
            plt.plot(list_thresh,list_precision,label=algo)
            plt.text(0.05,0.05+n/20,"Algorithm: "+algo+" Average precision= "+str(np.around(AP,2)))

    plt.xlabel("IOU",fontsize=20)
    plt.ylabel("Precision",fontsize=20)
    plt.ylim(0)
    plt.xlim(0)
    plt.legend(fontsize=20)
    plt.savefig(path_file+title+".png")
    return dico_algo_ap


def percentage_in_out(list_marker=["DNA"],path_img="./images/raw_images",path_mask="./mask_roi",path_file="./"):
    dico_algo_in_out={}
    list_name_img=os.listdir(path_img)
    for algo in os.listdir(path_mask):
        list_perc=[]
        for name_img in list_name_img: 
            sum_in=0
            sum_out=0
            for marker in list_marker:
                mask= np.array(Image.open(path_mask+"/"+algo+"/"+name_img+".tif"))
                img= np.array(Image.open(path_img+"/"+name_img+"/"+marker+".png"))
                img_in=np.where(mask>0,img,0)
                img_out=np.where(mask==0,img,0)
                sum_in+=np.sum(img_in)
                sum_out+=np.sum(img_out)
                list_perc.append(sum_in/(sum_in+sum_out)*100)
        dico_algo_in_out[algo]=list_perc
    plt.figure(figsize=(30,15))
    width=0.8/(len(dico_algo_in_out.keys()))
    for i,k in enumerate(dico_algo_in_out.keys()):
        if i==0:
            x_axis=np.arange(len(list_name_img))
        else:
            x_axis=[x + width for x in x_axis] 
        plt.bar(x_axis,dico_algo_in_out[k],label=k,width=width)
        
    plt.title("Percentage of marker intensity present into the masks",fontsize=35)
    plt.ylabel("Percentage",fontsize=30)
    plt.xlabel("Images",fontsize=30)
    plt.xticks([r + width for r in range(len(list_name_img))],list_name_img,rotation=70)
    plt.legend(fontsize=20)
    #plt.text(3,np.max(list(dico_roi_ratio.values())),"Mean percentage= "+str(mean_ratio),fontsize=15)
    plt.savefig(path_file+"percentage_marker_in.png")
    #return mean_ratio,dico_roi_ratio

    list_mean=[]
    for k in dico_algo_in_out.keys():
        list_mean.append(np.mean(dico_algo_in_out[k]))
    plt.figure()
    x_axis=np.arange(len(dico_algo_in_out.keys()))
    width=0.8/(len(dico_algo_in_out.keys()))
    plt.bar(x_axis,list_mean,color=["r","g","b"],width=width)
    for m in range(len(list_mean)):
        plt.text(m-0.1,20,"Mean: "+str(np.around(list_mean[m],2)))
    plt.title("Percentage of marker intensity present into the masks",fontsize=10)
    plt.ylabel("Percentage",fontsize=10)
    plt.xlabel("Images",fontsize=15)
    plt.xticks(x_axis,dico_algo_in_out.keys(),rotation=70)
    plt.savefig(path_file+"mean_marker_in.png")


def labels_to_features(lab: np.ndarray, object_type='annotation', connectivity: int=4, 
                      transform: Affine=None, mask=None, downsample: float=1.0, include_labels=False,
                      classification=None):
    """
    Create a GeoJSON FeatureCollection from a labeled image.
    """
    features = []
    
    # Ensure types are valid
    if lab.dtype == bool:
        mask = lab
        lab = lab.astype(np.uint8)
    else:
        mask = lab > 0
    
    # Create transform from downsample if needed
    if transform is None:
        transform = Affine.scale(downsample)
    
    # Trace geometries
    for s in rasterio.features.shapes(lab, mask=mask, 
                                      connectivity=connectivity, transform=transform):

        # Create properties
        props = dict(object_type=object_type)
        if include_labels:
            props['measurements'] = [{'name': 'Label', 'value': s[1]}]
            
        # Just to show how a classification can be added
        if classification is not None:
            props['classification'] = classification
        
        # Wrap in a dict to effectively create a GeoJSON Feature
        po = dict(type="Feature", geometry=s[0], properties=props)

        features.append(po)
    
    return features

def write_file(path_txt,text):
    with open(path_txt,'a') as f:
        f.write(text)

def script_ground_truth(path_img,path_mask,path_file="./",threshold=0.5,step=5):

    if os.path.isdir(path_file+"segmentation_quality")==False:
        os.mkdir(path_file+"segmentation_quality")

    path_txt=path_file+"segmentation_quality/summary.txt"
    path_file=path_file+"segmentation_quality"

    #sys.stdout = open('./segmentation_quality/summarize.txt', 'w')

    #distribution of the size of mask objects done manually
    size_distribution(path_mask,path_file,title="size_distribution.png")

    distribution_number_object(path_img=path_img,path_mask=path_mask,path_file=path_file,title="number_objects.png")

    #iou calculation without filter
    write_file(path_txt,"Evaluation of the algorithm without size filter\n")
    for algo in os.listdir(path_mask):
        if algo!="truth":
            list_iou=[]
            list_precision=[]
            list_recall=[]
            list_true_pos=[]
            list_false_pos=[]
            list_false_neg=[]
            dico_algo_ap=calcul_auc(path_img,path_mask)
            for file_img,file_mask in zip(os.listdir(path_img),os.listdir(path_mask+"/"+algo)):
                iou,dico_objet,df_mask,df_truth=calcul_iou(path_img+"/"+file_img,path_mask+"/"+algo+"/"+file_mask,path_mask+"/truth/"+file_mask)
                list_iou.append(iou)
                recall,precision,true_pos,false_pos,false_neg=recall_precision(threshold,df_mask,df_truth)
                list_precision.append(precision)
                list_recall.append(recall)
                list_true_pos.append(true_pos)
                list_false_pos.append(false_pos)
                list_false_neg.append(false_neg)
            write_file(path_txt,"*"*50+"\n")
            write_file(path_txt,algo+"\n")
            write_file(path_txt,"*"*50+"\n")
            write_file(path_txt,"Mean IOU= "+str(np.mean(list_iou))+" (without size filter)\n")
            write_file(path_txt,"Average precision: "+str(dico_algo_ap[algo])+"\n")
            write_file(path_txt,"\n")
            write_file(path_txt,"Number of predicted objects: "+str(np.sum(list_true_pos)+np.sum(list_false_pos))+"\n")
            write_file(path_txt,"Real object number: "+str(np.sum(list_true_pos)+np.sum(list_false_neg))+"\n")
            #recall, precision, true positives
            write_file(path_txt,"\n")
            write_file(path_txt,"For an IOU threshold= "+str(threshold)+" :\n")
            write_file(path_txt,"   Recall= "+str(np.mean(list_recall))+"\n")
            write_file(path_txt,"   Precision= "+str(np.mean(list_precision))+"\n")
            write_file(path_txt,"   Number of true positive= "+str(np.sum(list_true_pos))+"\n")
            write_file(path_txt,"   Number of false positive= "+str(np.sum(list_false_pos))+"\n")
            write_file(path_txt,"   Number of false negative= "+str(np.sum(list_false_neg))+"\n")
            write_file(path_txt,"\n")

    #calculation of the minimum and maximum size of the predicted mask objects that must be filtered
    #max_size,iou=
    dico_algo_max=calcul_max_size(path_img,path_mask,path_file,step)
    #calculation of the minimum and maximum size of the predicted mask objects that must be filtered
    dico_algo_min=calcul_min_size(path_img,path_mask,path_file,step)

    dico_algo_ap=calcul_auc(path_img,path_mask,path_file,dico_algo_min,dico_algo_max)

    #distribution of the size of mask objects with size filter
    size_distribution(path_mask,path_file,dico_algo_min,dico_algo_max,title="size_distribution_filtered.png")
    distribution_number_object(path_img=path_img,path_mask=path_mask,path_file=path_file,dico_algo_max=dico_algo_max,dico_algo_min=dico_algo_min,title="number_objects_filtered.png")

    write_file(path_txt,"\n"*3)
    write_file(path_txt,"Evaluation of the algorithm with a size filter\n")
    write_file(path_txt,"\n")
    for algo in os.listdir(path_mask):
        if algo!="truth":
            list_iou=[]
            list_recall=[]
            list_false_neg=[]
            list_true_pos=[]
            list_false_pos=[]
            list_precision=[]
            write_file(path_txt,"*"*100+"\n")
            write_file(path_txt,algo+"\n")
            write_file(path_txt,"*"*100+"\n")
            for file_img,file_mask in zip(os.listdir(path_img),os.listdir(path_mask+"/"+algo)):
                #calcul de l'iou et dictionnaire avec paire objet predit/manuel et l'iou en valeur
                iou,dico_objet,df_mask,df_truth=calcul_iou(path_img+"/"+file_img,path_mask+"/"+algo+"/"+file_mask,path_mask+"/truth/"+file_mask,dico_algo_min[algo],dico_algo_max[algo])
                list_iou.append(iou)
                recall,precision,true_pos,false_pos,false_neg=recall_precision(threshold,df_mask,df_truth)
                list_precision.append(precision)
                list_recall.append(recall)
                list_true_pos.append(true_pos)
                list_false_pos.append(false_pos)
                list_false_neg.append(false_neg)

            #Display of predicted masks colored according to the iou (iou<threshold: red, iou>threshold: blue)
            outline_iou(path_img+"/"+file_img,file_img,algo,df_mask,threshold,c=0)
            outline_iou(path_file+"outline_iou/"+algo+"/"+file_img[:-4]+".png",file_img[:-4]+".png",algo,df_truth,threshold,c=255)

            #Display of predicted masks colored and the outline of the ground truth
            outline_mask_color(path_img,path_mask,path_file,algo,dico_algo_min[algo],dico_algo_max[algo])
            write_file(path_txt,"Algorithme: "+algo+"\n")
            write_file(path_txt,"Best IOU= "+str(np.mean(list_iou))+" by filtering objects <"+str(dico_algo_min[algo])+" pixels and >"+str(dico_algo_max[algo])+"\n")
            write_file(path_txt,"Average precision: "+str(dico_algo_ap[algo])+"\n")
            write_file(path_txt,"\n")
            write_file(path_txt,"Number of predicted objects: "+str(np.sum(list_true_pos)+np.sum(list_false_pos))+"\n")
            write_file(path_txt,"Real object number: "+str(df_truth.shape[0])+"\n")

            #Calcul recall, precision, true positivess
            write_file(path_txt,"for a IOU threshold= "+str(threshold)+" :\n")
            write_file(path_txt,"   Recall= "+str(np.around(np.mean(list_recall),2))+"\n")
            write_file(path_txt,"   Precision= "+str(np.around(np.mean(list_precision),2))+"\n")
            write_file(path_txt,"   Number of true positive= "+str(np.sum(list_true_pos))+"\n")
            write_file(path_txt,"   Number of false positive= "+str(np.sum(list_false_pos))+"\n")
            write_file(path_txt,"   Number of false negative= "+str(np.sum(false_neg))+"\n")
            write_file(path_txt,"\n")


    #sys.stdout.close()
    #os.close(sys.stdout.fileno())

