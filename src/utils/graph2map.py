"""
graph2map.py
Autor: HyeongwonKang

community detection 결과를 folium map으로 visualization
예시 : 

(1) python graph2map.py -C /tf/dsba/lecture/2021_1/PGM/project/result/case4_duration_local_covid/node_per_class -E /tf/dsba/lecture/2021_1/PGM/project/result/case4_duration_local_covid/node_edge_d

(2) python graph2map.py -C /tf/dsba/lecture/2021_1/PGM/project/result/case4_duration_local_covid/node_per_class -E /tf/dsba/lecture/2021_1/PGM/project/result/case4_duration_local_covid/node_edge_d -M 51.5072 -0.1275 -Z 12 -T 50
"""

import folium
from folium import plugins
import pandas as pd
import numpy as np
import sys
import json
import argparse
import os
from os.path import isfile, join
import yaml
import re


def printProgressBar(iteration, total, prefix = 'Progress', suffix = 'Complete',\
                      decimals = 1, length = 70, fill = '█'):
    # 작업의 진행상황을 표시
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    _string_out = '\r%s |%s| %s%% %s' %(prefix, bar, percent, suffix)
    sys.stdout.write(_string_out)
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write('\n')

def load_data(path):
    if re.search(r"csv", path) != None:
        data = pd.read_csv(path)
    elif re.search(r"pkl", path) != None:
        data = pd.read_pickle(path)
    else:
        print('file load error')
        
    return data          
        
def cd_visualization(geo, 
                     stations,
                     node_class, 
                     node_edge,
                     output_path,
                     colors: list, 
                     center: list=[51.5072, -0.1275], 
                     zoom: int=13, 
                     threshold: int=50):
    """
    community detection map visualization
    
    Arguments
    ---------
    - geo         : geoJson,
    - stations    : london stations info,
    - node_class  : community detection node class, 
    - node_edge   : community detection node edge, 
    - output_path : path to save the visualized map,
    - colors      : colors,
    - center      : center of map {default: [51.5072, -0.1275]},
    - zoom        : zoom size {default: 12}
    - threshold   : threshold {default: 50}
    
    Return
    ------
    None
    """
    
    
    print(f'start! task : {output_path}')
    
    map_osm = folium.Map(location=center, tiles='cartodbpositron', zoom_start=zoom)
    
    folium.GeoJson(
        geo,
        name='london_municipalities',
        style_function = lambda x: {'fill': False}
        ).add_to(map_osm)

    for i, c in enumerate(node_edge.index):
        printProgressBar(i+1, len(node_edge.index))
        if node_edge.loc[c, 'source'] != node_edge.loc[c, 'target']:
            if node_edge.loc[c, 'value'] >= threshold:
                source = [stations[stations['station_id']==node_edge.loc[c, 'source']]['latitude'].item(),
                    stations[stations['station_id']==node_edge.loc[c, 'source']]['longitude'].item()]
                target = sourge = [stations[stations['station_id']==node_edge.loc[c, 'target']]['latitude'].item(),
                    stations[stations['station_id']==node_edge.loc[c, 'target']]['longitude'].item()]
                points = [source, target]
                folium.PolyLine(points, color="black", 
                                weight=node_edge.loc[c, 'value']*0.01, opacity=0.5).add_to(map_osm)
            else:
                pass
        else:
            pass
    
    
    for i, c in enumerate(node_class.keys()):
        printProgressBar(i+1, len(node_class.keys()))
        for s in node_class[c]:
            folium.CircleMarker(
                [stations[stations['station_id']==s]['latitude'].item(),
                stations[stations['station_id']==s]['longitude'].item()],
                radius = 1,
                color=colors[i],
                fill_color=colors[i],
            ).add_to(map_osm)
            
    map_osm.save(output_path)
    print(f'save complete!')             


if __name__ == "__main__":
    
    
    with open('config.yaml') as f:
        config = yaml.load(f)
        
    pathOut = config['pathOut']
    colors = config['colors']
    station_info = config['station_info']
    
    ap = argparse.ArgumentParser()
    ap.add_argument("-C", "--class_files_path", required=True, help="node_class path")
    ap.add_argument("-E", "--edge_files_path", required=True, help="node_edge path")
    ap.add_argument("-M", "--map_center", default=[51.5072, -0.1275], nargs='+', type=float, help="map center")
    ap.add_argument("-Z", "--zoom", default=13, type=int, help="zoom size")
    ap.add_argument("-T", "--threshold", default=50, type=int, help="threshold")

    args = vars(ap.parse_args())

    class_files_path = args["class_files_path"]
    edge_files_path = args["edge_files_path"]
    map_center = args["map_center"]
    zoom = args["zoom"]
    threshold = args["threshold"]
    
    # path out folder 없는 경우 생성
    if not os.path.exists(pathOut):
        os.makedirs(pathOut)
    else:
        print(pathOut + " has been processed!")
    
    with open(config['geo_path'], mode='rt',encoding='utf-8') as f:
        geo = json.loads(f.read())
        f.close()
        
    stations = load_data(config['station_path'])
    
    class_files = [f for f in os.listdir(args["class_files_path"]) if isfile(join(class_files_path, f))]
    class_files.sort()
    edges_files = [f for f in os.listdir(args["edge_files_path"]) if isfile(join(edge_files_path, f))]
    edges_files.sort()
    
    for i in range(len(class_files)):
        class_file = load_data(join(class_files_path, class_files[i]))
        edges_file = load_data(join(edge_files_path, edges_files[i]))
        output_path = join(pathOut, re.search(r"(\w+)\.(\w+)", class_files[i]).group(1))+'.html'
                
        cd_visualization(geo, stations, class_file, edges_file, output_path, colors, map_center, zoom, threshold)

