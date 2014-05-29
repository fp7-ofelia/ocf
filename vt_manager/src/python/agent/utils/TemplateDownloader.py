#!/usr/bin/env python

"""
Loads list of VM templates in order to download those.

@date: May 7, 2014
@author: CarolinaFernandez
"""

import math
import os
import subprocess
import sys

class TemplateDownloader():

    def __init__(self, *args, **kwargs):
        self._template_server = "ftp://84.88.40.11"
        self._templates_basepath = "/opt/ofelia/oxa/cache/templates"
        self._ofelia_templates_path = "ofelia/"
        self._non_ofelia_templates_path = "non-ofelia/"
        self._curl = self.execute(["which", "curl"])[0].strip()
        self._wget = self.execute(["which", "wget"])[0].strip()
        self.__dict__.update(self.arg_parse(args))
        self._chosen_templates = []
        # Store templates info
        self.cache_templates_info()
    
    def arg_parse(self, arguments):
        import argparse
        # Arguments from constructor come with a different format
        arguments = arguments[0]
        def find(lst, predicate):
            return next((i for i,j in enumerate(lst) if predicate(j)), -1)

        parser = argparse.ArgumentParser(description="")
        parser.add_argument("--ofelia", help="OFELIA (True) or Non-OFELIA (False) installation",
                        type=int, default=1, required=True, choices=[1, 0])
        parser.add_argument("--save-path", help="Path where templates are saved",
                        type=str, default=self._templates_basepath, required=False)
        args = parser.parse_args(arguments)
        # Return parsed Namespace as a dictionary
        args = args.__dict__
        # Rename variables in dictionary
        for old_key in args.keys():
            if old_key == "save_path":
                args["templates_basepath"] = args[old_key]
            new_key = "_%s" % old_key
            args[new_key] = args.pop(old_key)
        return args
    
    def execute(self, command_list):
        process = subprocess.Popen(command_list, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Wait for the process to terminate
        out, err = process.communicate()
        return (out, err)
    
    def curl(self, uri, silent=True):
        command_list = []
        command_list.append(self._curl)
        command_list.append(uri)
        if silent:
            command_list.append("--silent")
        return self.execute(command_list)
    
    def wget(self, uri, folder_path):
        command_list = []
        command_list.append(self._wget)
        command_list.append(uri)
        command_list.append("-O")
        command_list.append(os.path.join(self._templates_basepath, folder_path))
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
        # FIXME Fix data format. Uncomment later. Test with dummy data to avoid reconnections to FTP.
        return self.curl(os.path.join(self._template_server, "%s/" % folder_path))
    
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
    def get_templates(self):
        if self._ofelia:
            return self.get_ofelia_templates()
        else:
            return self.get_non_ofelia_templates()

    def get_templates_info(self):
        if self._ofelia:
            return self.get_ofelia_templates_info()
        else:
            return self.get_non_ofelia_templates_info()

    def get_ofelia_templates(self):
        return self.get_contents_from_folder(self._ofelia_templates_path)

    def get_ofelia_templates_info(self):
        ofelia_templates = self.get_ofelia_templates()
        ofelia_templates_info = []
        for template in ofelia_templates:
            ofelia_templates_info.append(self.get_info_from_folder(os.path.join(self._ofelia_templates_path, template)))
        return ofelia_templates_info

    def get_non_ofelia_templates(self):
        return self.get_contents_from_folder(self._non_ofelia_templates_path)

    def get_non_ofelia_templates_info(self):
        non_ofelia_templates = self.get_non_ofelia_templates()
        non_ofelia_templates_info = []
        for template in non_ofelia_templates:
            non_ofelia_templates_info.append(self.get_info_from_folder(os.path.join(self._non_ofelia_templates_path, template)))
        return non_ofelia_templates_info

    def cache_templates_info(self):
        templates_info = self.get_templates_info()
        self.templates_info_dict = dict()
        for template_number, template_info in enumerate(templates_info):
            template_no = "template%d" % (template_number+1)
            self.templates_info_dict[template_no] = dict()
            self.templates_info_dict[template_no]["number"] = template_number + 1
           
            hash_info = None
            temp_info = None
            try:
                if template_info[0][0].endswith(".hash"):
                    try:
                        hash_info = template_info[0]
                    except:
                        pass
                    try:
                        temp_info = template_info[1]
                    except:
                        pass
                else:
                    try:
                        hash_info = template_info[1]
                    except:
                        pass
                    try:
                        temp_info = template_info[0]
                    except:
                        pass
            except:
                pass
            
            # At some point, templates could lack its hash file. Ignore if that happens
            try:
                self.templates_info_dict[template_no]["hash"] = dict()
                self.templates_info_dict[template_no]["hash"]["filename"] = hash_info[0]
                self.templates_info_dict[template_no]["hash"]["size"] = hash_info[1]
            except:
                pass
            
            try:
                self.templates_info_dict[template_no]["template"] = dict()
                self.templates_info_dict[template_no]["template"]["filename"] = temp_info[0]
                self.templates_info_dict[template_no]["template"]["size"] = temp_info[1]
            except:
                pass

    # Menu
    def get_indent_for_template(self, template_name):
        if len(template_name) <= 15:
            indent = "\t\t\t"
        else:
            indent = "\t\t"
        return indent

    def show_menu(self, filtered_templates=None):
        import collections
        if isinstance(filtered_templates, list):
            if filtered_templates:
                show_dict = { "template%s" % temp_key: self.templates_info_dict["template%s" % temp_key] for temp_key in filtered_templates }
            else:
                show_dict = {}
        else:
            show_dict = self.templates_info_dict
        templates_info_ord = collections.OrderedDict(sorted(show_dict.items()))
        for template, template_data in templates_info_ord.iteritems():
#        for t in self.templates_info_dict.keys():
            sys.stdout.write("\n")
            # At some point, images could lack a hash file. Ignore if that happens
#            try:
#                template_number = self.templates_info_dict[t]["number"]
#                template_hash = self.templates_info_dict[t]["hash"]
#                indent = self.get_indent_for_template(template_hash["filename"])
#                sys.stdout.write("[%s] %s%s%s\n" % (str(template_number), str(template_hash["filename"]), indent, str(template_hash["size"])))
#            except:
#                pass
            try:
                template_number = template_data["number"]
                template_file = template_data["template"]
                # File extensions not shown
                template_filename = template_file["filename"].split(".")[0]
                indent = self.get_indent_for_template(template_file["filename"])
                sys.stdout.write("[%s] %s%s%s" % (str(template_number), str(template_filename), indent, str(template_file["size"])))
            except:
                pass

    # Download templates
    def download_template_file(self, uri, folder_path=None):
        full_download_path = os.path.realpath(os.path.join(self._templates_basepath, folder_path))
        # Get the parent directory where the file is to be saved...
        download_path = os.path.dirname(full_download_path)
        # If directory does not exist, create it before downloading anything
        if not os.path.isdir(download_path):
            os.makedirs(download_path)
        # Check if file exists prior to download
        if os.path.isfile(full_download_path):
            sys.stdout.write("\nFile at %s already exists. " % full_download_path)
            do_overwrite = self.ask_for_ok("Overwrite?")
            if not do_overwrite:
                return
        else:
            pass
        sys.stdout.write("\nDownloading file from %s. Please wait...\n" % uri)
        return self.wget(uri, os.path.join(self._template_server, folder_path))

    def download_template_files(self, template_dict_id):
        template_files = []
        template_files.append(self.templates_info_dict[template_dict_id]["hash"]["filename"])
        template_files.append(self.templates_info_dict[template_dict_id]["template"]["filename"])
        for template_file in template_files:
            template_name = template_file.split(".")[0]
            # Construct template URI depending on if it is an OFELIA installation or not
            if self._ofelia:
                template_uri = os.path.join(self._template_server, self._ofelia_templates_path, template_name, template_file)
            else:
                template_uri = os.path.join(self._template_server, self._non_ofelia_templates_path, template_name, template_file)
            # Download path is provided by the user -- otherwise default is used
            # It is generated from user's input and part of the information carried on the template itself
            download_path = os.path.join(self._templates_basepath, template_name, template_file)
            self.download_template_file(template_uri, download_path)
        # TODO Check that download is correct by checking .hash file

    def download_chosen_templates(self):
        # Get files per chosen template
        files_to_download = []
        for chosen_template in self._chosen_templates:
            self.download_template_files("template%s" % chosen_template)

    # Interaction with user
    def ask_for_templates_selection(self):
        # Ask for templates to be selected
        templates_selected = False
        while not templates_selected:
            # Parse contents from FTP and show
            self.show_menu()
            sys.stdout.write("\n\nSelect the templates to download by entering its number(s). Use spaces to separate")
            sys.stdout.write("\n\tExample: 1 3")
            sys.stdout.write("\n\tExample: all (select all the templates)")
            sys.stdout.write("\n\tExample: none (select no templates)\n\n")
            
            self._chosen_templates = []
            template_number_to_select = raw_input("select> ")
            template_number_to_select_parsed = []
            # Template numbers to select
            if template_number_to_select:
                if isinstance(template_number_to_select, str):
                    #template_number_to_select = [ int(t) for t in template_number_to_select.split(" ") ]
                    for template in template_number_to_select.split(" "):
                        try:
                            if not int(template) in template_number_to_select_parsed:
                                template_number_to_select_parsed.append(int(template))
                            template_number_to_select_parsed = self.ensure_existing_templates(template_number_to_select_parsed)
                        except:
                            try:
                                # XXX Parse special input ("all", "none")
                                if template == "all":
                                   all_templates = [ template for template in self.templates_info_dict.keys() ]
                                   all_templates = [ int(self.templates_info_dict[t]["number"]) for t in all_templates ]
                                   all_templates.sort()
                                   for template in all_templates:
                                       if not int(template) in template_number_to_select_parsed:
                                           template_number_to_select_parsed.append(template)
                                elif template == "none":
                                   template_number_to_select_parsed = []
                            except:
                                pass
                    self._chosen_templates = template_number_to_select_parsed
            else:
                break
            # Ensure that the chosen templates do exist within the templates dict
            template_number_to_select_parsed = self.ensure_existing_templates(template_number_to_select_parsed)
            # Show menu for selected templates
            sys.stdout.write("\nChosen templates:\n")
            self.show_menu(self._chosen_templates)
            sys.stdout.write("\n\n")
            templates_selected = self.ask_for_ok()
        return self._chosen_templates

    def ensure_existing_templates(self, list_template_numbers):
        filter_existing_templates = lambda x: x in [ self.templates_info_dict[k]["number"] for k in self.templates_info_dict.keys() ]
        return filter(filter_existing_templates, list_template_numbers)

    def ask_for_exit(self):
        do_exit = raw_input("Are you sure you want to quit? [y/N]: ")
        if do_exit in ["y", "Y"]:
            return True
        elif do_exit in ["n", "N"]:
            print "nooooooooooo exiting!"
            return False
        else:
            return self.ask_for_exit()

    def ask_for_ok(self, message=None):
        if not message:
            message = "Is everything OK?"
        is_ok = raw_input("%s [Y/n]: " % message)
        if is_ok in ["y", "Y"]:
            return True
        elif is_ok in ["n", "N"]:
            return False
        else:
            return self.ask_for_ok()


## TODO
# * Implemente checking of template.hash against downloaded hash after download (OR DELEGATE TO CRON JOB??)

def main():
    #template_downloader = TemplateDownloader(**template_arguments)
    template_downloader = TemplateDownloader(sys.argv[1:])
    try:
        template_downloader.ask_for_templates_selection()
        template_downloader.download_chosen_templates()
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print "EXCEPTION: ", e
        do_exit = template_downloader.ask_for_exit()
        if do_exit:
            sys.exit(do_exit)
    return True

if __name__ == "__main__":
    main()
