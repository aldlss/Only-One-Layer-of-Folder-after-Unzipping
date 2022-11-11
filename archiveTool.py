import argparse
import os
import py7zr,zipfile,tarfile
import shutil
import tqdm

def getNamelist(archiveName:str)-> list[str]:
    ext=os.path.splitext(archiveName)[1]
    if ext == ".zip":
        with zipfile.ZipFile(archiveName,"r") as z:
            nameList=z.namelist()
    elif ext==".7z":
        with py7zr.SevenZipFile(archiveName) as z:
            nameList=z.getnames()
    # elif ext==".rar":需要安装相关软件，放弃了
    #     with rarfile.RarFile(archiveName) as z:
    #         nameList=z.namelist()
    elif ext==".tar":
        with tarfile.TarFile(archiveName) as z:
            nameList=z.getnames()
    else:
        # raise ValueError ("Not supported extension.")
        return []
    fileSet=set()
    for name in nameList:
        surfaceName=name.split('/')[0]
        if fileSet.isdisjoint(f"{surfaceName}"):
            fileSet.add(surfaceName)
    return list(fileSet)

def clean(filesList:list[str]):
    for file in tqdm.tqdm(filesList,desc="cleaning"):
        nameList=getNamelist(file)
        if len(nameList)<=1:
            continue
        path=os.path.split(file)[0]
        for name in nameList:
            fullPath=os.path.join(path,name)
            if os.path.isdir(fullPath):
                shutil.rmtree(fullPath)
            elif os.path.isfile(fullPath):
                os.remove(fullPath)

def extract(filesList:list[str],overwrite:bool):
    for file in tqdm.tqdm(filesList,desc="extracting"):
        nameList=getNamelist(file)
        count=len(nameList)
        if count <=0:
            continue
        path=os.path.split(file)[0]
        if(count==1):
            if os.path.exists(nameList[0]):
                if not overwrite:
                    continue
                elif os.path.isdir(file):
                    shutil.rmtree(file)
            shutil.unpack_archive(file,path)
        else:
            dirPath=os.path.splitext(file)[0]
            if os.path.isdir(dirPath):
                if overwrite:
                    shutil.rmtree(dirPath)
                else:
                    continue
            os.mkdir(dirPath)
            shutil.unpack_archive(file,dirPath)
    
def initializeExtract():
    # register file format at first.
    shutil.register_archive_format('7zip', py7zr.pack_7zarchive, description='7zip archive')
    shutil.register_unpack_format('7zip', ['.7z'], py7zr.unpack_7zarchive)

def main():
    parser=argparse.ArgumentParser(description="archiveTool")
    parser.add_argument("--clean",action="store_true",help="clean up the wrong extractd members")
    parser.add_argument("--extract",action="store_true",help="extract all members from the archive in each package separately into a folder")
    parser.add_argument("--overwrite",action="store_true",help="remove then extract if there is a folder with the same name when extracting")
    parser.add_argument("--path",type=str,help="the archived files' path",default="")
    args=parser.parse_args()
    if os.path.isdir(args.path) or os.path.isfile(args.path):
        path=args.path
    else:
        path=os.path.join(os.getcwd(),args.path)
        if not (os.path.isdir(path) or os.path.isfile(path)):
            assert ValueError,"can't find such path"
    
    if(os.path.isdir(path)):#确保给的是绝对路径        
        filesList=os.listdir(path)
        for idx,file in enumerate(filesList):
            filesList[idx]=os.path.join(path,file)
    else:
        filesList=[path]
    
    # print(filesList)

    if args.clean:
        clean(filesList)
    if args.extract:
        initializeExtract()
        extract(filesList,args.overwrite)

if __name__ =="__main__":
    main()