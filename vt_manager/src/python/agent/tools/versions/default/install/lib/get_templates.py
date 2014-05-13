#!/usr/bin/env python

"""
Loads list of VM templates in order to download those.

@date: May 7, 2014
@author: CarolinaFernandez
"""

import math
import subprocess

class TemplateDownloader():

    def __init__(self):
        self.__template_server = "ftp://84.88.40.11"
        self.__ofelia_templates_path = "ofelia/"
        self.__non_ofelia_templates_path = "non-ofelia/"
        self.__curl = self.execute(["which", "curl"])[0].strip()
        self.__wget = self.execute(["which", "wget"])[0].strip()
    
    def execute(self, command_list):
        process = subprocess.Popen(command_list, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Wait for the process to terminate
        out, err = process.communicate()
        return (out, err)
    
    def curl(self, uri, silent=True):
        command_list = []
        command_list.append(self.__curl)
        command_list.append(uri)
        if silent:
            command_list.append("--silent")
        return self.execute(command_list)
    
    def convert_size(self, size):
        size = int(size)
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size,1024)))
        p = math.pow(1024,i)
        s = round(size/p,2)
        if (s > 0):
            return "%s %s" % (s,size_name[i])
        else:
            return "0B"
    
    def list_folder(self, folder_path=""):
        return self.curl("%s/%s/" % (self.__template_server, folder_path))
    
    def get_info_from_folder(self, folder_path=""):
        """
        Retrieve size and filenames from a given path.
        """
        contents_info = self.list_folder(folder_path)[0]
        contents_info = contents_info.split()
        contents_info_sublists = []
        i = 0
        for info_item in contents_info:
            i+=1
            if i%9 == 0:
                contents_info_sublists.append(contents_info[i-9:i])
        contents_info = []
        for content_info_sublist in contents_info_sublists:
            # (template_name, template_size)
            contents_info.append((content_info_sublist[-1], self.convert_size(content_info_sublist[4])))
        return contents_info
    
    def get_contents_from_folder(self, folder_path=""):
        """
        Retrieve filenames from a given path.
        """
        contents_info = self.get_info_from_folder(folder_path)
        return [ x[0] for x in contents_info ]
    
    
    # Specific methods
    def get_ofelia_templates(self):
        return self.get_contents_from_folder(self.__ofelia_templates_path)

    def get_ofelia_templates_info(self):
        ofelia_templates = self.get_ofelia_templates()
        ofelia_templates_info = []
        for template in ofelia_templates:
            ofelia_templates_info.append(self.get_info_from_folder("%s/%s" % (self.__ofelia_templates_path, template)))
        return ofelia_templates_info

    def get_non_ofelia_templates(self):
        return self.get_contents_from_folder(self.__non_ofelia_templates_path)

    def get_non_ofelia_templates_info(self):
        non_ofelia_templates = self.get_non_ofelia_templates()
        non_ofelia_templates_info = []
        for template in non_ofelia_templates:
            non_ofelia_templates_info.append(self.get_info_from_folder("%s/%s" % (self.__non_ofelia_templates_path, template)))
        return non_ofelia_templates_info


def main():
    template_downloader = TemplateDownloader()
    print "OFELIA templates:\n %s" % template_downloader.get_ofelia_templates_info()
    print "non-OFELIA templates:\n %s" % template_downloader.get_non_ofelia_templates_info()
    return True

if __name__ == "__main__":
    main()

