from identity_clustering.cluster import detect_faces, FaceCluster, cluster
from identity_clustering.utils import _get_crop
from .Inference import Inference
import numpy as np
import os
import tqdm
import cv2 as cv
def detect_probable_fakes(mask_frame, bbox, threshold = 0.50):
    mask = _get_crop(mask_frame,bbox, pad_constant=4)
    tot = mask.shape[0] * mask.shape[1]
    blob = np.sum(mask)
    if blob == 0.:
        return 1.
    
    fake_prob = blob/tot
    if fake_prob >= threshold:
        return 0.
    else:
        return 1.
def prepare_data(root_dir, save_dir, mask_dir, min_num_frames = 10):
    inf = Inference("cuda")
    clust = FaceCluster()
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    save_idx = 0

    for video_file in tqdm.tqdm(os.listdir(root_dir)):

        video_path = os.path.join(root_dir, video_file)
        mask_path = os.path.join(mask_dir, video_file[:-4] + "_mask.mp4")
        faces, fps = detect_faces(video_path,"cuda")
        clu = cluster(clust,video_path,faces,50)
        vid = cv.VideoCapture(mask_path)
        frames = []
        while True:
            success, frame = vid.read()
            if not success:
                break
            frames.append(cv.cvtColor(frame, cv.COLOR_BGR2GRAY))
        
        for key, value in clu.items():

            if len(value) < min_num_frames:
                continue

            label = None
            for i in value:
                frame_idx = i[0]
                curr_mask = frames[frame_idx]
                if label == None or label == 1:
                    label = detect_probable_fakes(curr_mask, i[2], 0.3)
            
            identity_tensor = inf.cvt_to_rgb(value)
            identity_tensor = identity_tensor.numpy()
            arr = np.array(identity_tensor)
            arr_label = np.array(label)
            np.save(os.path.join(save_dir, str(save_idx) + ".npy"),arr)
            np.save(os.path.join(save_dir,str(save_idx)+"_label.npy"),arr_label)
            save_idx += 1