"""
 Copyright (C) 2025  sophie (itsme@itssophi.ee)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import shutil
import glob
import re
import json
import time

class Build():
    def __init__(self):
        self._source = "./src" 
        self._destination = "./public"
        self.template_prefix = "_._"
        self.regex_placeholder = r"\{\{[^}]*\}\}"
        self.placeholder_elements = ["{", "}"]
        self.no_output = False
        self.pattern_prefix = r"{s{" #the one for doing the thing with templates
        self.pattern_suffix = r"}}"  # filled with data from the json
        self._template_version = "1.0.0"
        self.skip_invalid_placeholders = False
        self.debug_print = False
        self.prefer_1 = True # see where used

    @property
    def source(self):
        return self._source
    
    @source.setter
    def source(self, sourcee:str):
        self._source = "./" + sourcee.replace("./", "")

    @property
    def destination(self):
        return self._destination

    @destination.setter
    def destination(self, destinationn:str):
        self._destination = "./" + destinationn.replace("./", "")

    def start(self):
        if not self.no_output:
            start_time = time.perf_counter() #no point calculating if not shown to user
            print("Building…")

        p = re.compile(self.regex_placeholder)
        
        try:
            shutil.rmtree(self.destination)
        except FileNotFoundError:
            pass #the directory isn't there yet, normal case on first use
        shutil.copytree(self.source, self.destination)

        if self.debug_print:
                print(f"self.prefer_1: {self.prefer_1}")
        if self.prefer_1: #either make all includes first, then the rest
            includes = self._find_includes(self.template_prefix)

            if self.debug_print:
                print(f"\nFound includes: {includes}")
            
            file_paths_wo_includes = self._find_rest_files(includes)

            if self.debug_print:
                print(f"\nFound paths wo includes: {file_paths_wo_includes}")

            # first, it replaces every placholder in the files that should be filled that
            # way, then the rest. This allows faster processing for nested includes as so
            # that the same includes don't get processed twice (in a 1 level nesting).
            self._check_and_replace(includes, p)
            self._check_and_replace(file_paths_wo_includes, p)
        else: #or all at the same time. 
            # Aka either find include files and less regex matching, 
            # or no include file finding and more regex matching
            self._check_and_replace(self._find_all_files(), p)

        if not self.no_output:
            middle_time = time.perf_counter()
            m_execution_time = int((middle_time - start_time)*1000)
            print(f"Placeholer part completed in {m_execution_time}ms")

        # the templating stuff with the json file to fill data
        blueprints = self._find_blueprints("bombhtml-template")

        for i in blueprints:
            data = self._read_blueprint_file(i)
            if self._template_version != data["version"]:
                raise ValueError(f"Invalid config version: {data['version']}. Expected: {self._template_version}.")
            path = self.destination +"/" + data["template"].replace("./", "")
            content = data["template-content"]
            new_path = i.replace(".json", "")
            shutil.copyfile(path, new_path)
            for name, value in content.items():
                with open(new_path, "r") as file_content:
                    new_file_content = file_content.read().replace(self.pattern_prefix + name + self.pattern_suffix, value)
                with open(new_path, "w") as file_cont:
                    file_cont.write(new_file_content)

            os.remove(i)

        self._remove_includes(self.template_prefix)

        if not self.no_output:
            final_time = time.perf_counter()
            f_execution_time = int((final_time - middle_time)*1000)
            tot_execution_time = int((final_time - start_time)*1000)
            print(f"Templating part completed in {f_execution_time}ms")
            print(f"Total completed in {tot_execution_time}ms")

    def _find_includes(self, template_prefix:str):
        includes = []
        for i in self._find_templates(template_prefix):
            if self._is_textfile(i):
                includes.append(i)
            elif os.path.isdir(i):
                for y in self._findall(i):
                    if self._is_textfile(y):
                        includes.append(y)
            else:
                raise FileNotFoundError(f"{i} isn't a text file or directory. Or at least I am unable to read it.")

        return includes

    def _find_rest_files(self, includes):
        file_paths_wo_includes = []
        for i in self._find_all_files():
            if i not in includes:
                file_paths_wo_includes.append(i)
        return file_paths_wo_includes
        

    def _find_all_files(self): #only files no dirs
        file_paths = []
        for i in self._findall(self.destination):
            if self._is_textfile(i):
                file_paths.append(i)

        return file_paths

    def _find_templates(self, template_prefix:str):
        formatted_path = self.destination + "/**/" + template_prefix + "*"
        return glob.glob(formatted_path, recursive=True)

    def _findall(self, directory:str):
        formatted_path = directory + "/**/*"
        return glob.glob (formatted_path, recursive = True)

    def _remove_includes(self, template_prefix):
        for i in self._find_templates(template_prefix):
            if os.path.isdir(i):
                shutil.rmtree(i)
            elif os.path.isfile(i):
                os.remove(i)
            else:
                raise FileNotFoundError(f"FATAL: {i} should have been raised as no text file before but it didn't happen.")

    def _is_textfile(self, path:str):
        if os.path.isfile(path):
            with open(path, "r") as i_file:
                try:
                    i_file.read()
                except:
                    return False
                else:
                    return True
        
        return False
    
    def _check_and_replace(self, paths:list[str], p:re.Pattern):
        for path in paths:
            if self.debug_print:
                print(f"\npath: {path}")
            with open(path, "r") as file_r:
                regex_matches = p.findall(file_r.read())
            if not regex_matches:
                if self.debug_print:
                    print("no match")
                pass
            else:
                if self.debug_print:
                    print("match")
                for i in regex_matches:
                    try:
                        if self.debug_print:
                            print(i)
                        x = i.replace("./", "")
                        for j in self.placeholder_elements:
                            x = x.replace(j, "")
                        with open(self.destination + "/" + x, "r") as filler:
                            filler_str = filler.read()
                            if not p.findall(filler_str):# if there are no placeholders in filler
                                if self.debug_print:
                                    print("executing")
                                with open(path, "r") as file_r:
                                    file_r_before = file_r.read()
                                with open(path, "w") as file_w:
                                    file_w.write(file_r_before.replace(i, filler_str))
                            else: # if there are, do it later.
                                if self.debug_print:
                                    print("skipping")
                                if not paths[-1] == path:
                                    paths.append(path)
                    except Exception as e:
                        if not self.skip_invalid_placeholders:
                            raise TypeError(f"{i} located in {path} isn't a valid placeholder. This mostly means that the path is wrongly formatted. More info: {e}")
                        print(f"WARN: {i} located in {path} isn't a valid placeholder. This mostly means that the path is wrongly formatted (whole file skipped). More info: {e}")

    def _is_jsonfile(self, path:str):
        if self._is_textfile(path):
            if path.endswith(".json"):
                with open(path, "r") as json_file:
                    try:
                        json.load(json_file)
                    except:
                        return False
                    else:
                        return True
        
        return False
    
    def _find_jsons(self, file_paths:list[str]):
        jsons = []
        for i in file_paths:
            if self._is_jsonfile(i):
                jsons.append(i)

        return jsons

    def _read_blueprint_file(self, path):
        with open(path, "r") as jfile:
            data = json.load(jfile)
        return data

    def _find_blueprints(self, json_type):
        blueprints = []
        jsons = self._find_jsons(self._find_all_files())
        for i in jsons:
            data = self._read_blueprint_file(i)
            if data["type"] == json_type: #the field equals the one we want
                blueprints.append(i)
        return blueprints

