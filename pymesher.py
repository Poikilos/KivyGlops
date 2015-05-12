"""
This provides simple dependency-free access to OBJ files and certain 3D math operations.
#Illumination models (as per OBJ format standard):
# 0. Color on and Ambient off
# 1. Color on and Ambient on [binary:0001]
# 2. Highlight on [binary:0010]
# 3. Reflection on and Ray trace on [binary:0011]
# 4. Transparency: Glass on, Reflection: Ray trace on [binary:0100]
# 5. Reflection: Fresnel on and Ray trace on [binary:0101]
# 6. Transparency: Refraction on, Reflection: Fresnel off and Ray trace on [binary:0110]
# 7. Transparency: Refraction on, Reflection: Fresnel on and Ray trace on [binary:0111]
# 8. Reflection on and Ray trace off [binary:1000]
# 9. Transparency: Glass on, Reflection: Ray trace off [binary:1001]
# 10. Casts shadows onto invisible surfaces [binary:1010]
"""

import os
import math
#from docutils.utils.math.math2html import VerticalSpace

#references:
#kivy-trackball objloader (version with no MTL loader) by nskrypnik
#objloader from kivy-rotation3d (version with placeholder mtl loader) by nskrypnik

#TODO:
#-remove resource_find but still make able to find mtl file under Kivy somehow

from kivy.resources import resource_find

class PyMesherMaterial:
    properties = None
    name = None
    mtlFileName = None  #required so that references to materials work properly
    
    def __init__(self):
        self.properties = {}
        
    def dump(self, thisList, tabStringMinimum):
        thisList.append(tabStringMinimum+"material:")
        tabString="  "
        if self.name is not None:
            thisList.append(tabStringMinimum+tabString+"name: "+self.name)
        if self.mtlFileName is not None:
            thisList.append(tabStringMinimum+tabString+"mtlFileName: "+self.mtlFileName)
        for k,v in sorted(self.properties.items()):
            thisList.append(tabStringMinimum+tabString+k+": "+str(v))


def dumpAsYAMLArray(thisList, thisName, sourceList, tabStringMinimum):
    tabString="  "
    thisList.append(tabStringMinimum+thisName+":")
    for i in range(0,len(sourceList)):
        thisList.append(tabStringMinimum+tabString+"- "+str(sourceList[i]))
    

class PyMesherMesh:
    name = None #object name such as from OBJ's 'o' statement
    objFileName = None  #required so that meshes can be uniquely identified (where more than one file has same object name)
    properties = None #dictionary of properties--has indices such as usemtl
    vertex_depth = None
    material = None
    
    #region raw OBJ data
    _vertex_strings = None
    _obj_cache_vertices = None
    _pivot_point = None
    texcoords = None
    normals = None
    parameter_space_vertices = None  #only for curves--not really implemented, just loaded from obj
    faces = None
    #endregion raw OBJ data
    
    vertex_format = None
    vertices = None
    indices = None
    diffuse_color = None
    ambient_color = None
    specular_color = None
    specular_coefficent = None
    opacity = None #formerly opacity
    
    def __init__(self):
        self.properties = {}
        self._vertex_strings = []
        self.texcoords = []
        self.normals = []
        self.parameter_space_vertices = []
        self.faces = []
        self.vertex_depth = 8
        #formerly in MeshData:
        self.vertex_format = [
            (b'v_pos', 3, 'float'),
            (b'v_normal', 3, 'float'),
            (b'v_tc0', 2, 'float')]
        self._obj_cache_vertices = []
        self.indices = []

        # Default basic material of mesh object
        self.diffuse_color = (1.0, 1.0, 1.0)
        self.ambient_color = (1.0, 1.0, 1.0)
        self.specular_color = (1.0, 1.0, 1.0)
        self.specular_coefficent = 16.0
        self.opacity = 1.0

    def _on_change_pivot(self):
        pass
       
    def transform_pivot_to_geometry(self):
        self._pivot_point = self.get_center_average_of_vertices()
        self._on_change_pivot()
        pass
    
    def getTextureFileName(self):
        fileName = None
        try:
            if self.material is not None:
                fileName = self.material.properties["map_Kd"]
        except:
            pass  #don't care
        return fileName

    def get_center_average_of_vertices(self):
        #results = (0.0,0.0,0.0)
        totals = list()
        counts = list()
        results = list()
        results.append(0.0)
        results.append(0.0)
        results.append(0.0)
        participle = "before initializing"
        try:
            totals.append(0.0)
            totals.append(0.0)
            totals.append(0.0)
            counts.append(0)
            counts.append(0)
            counts.append(0)
            if (self.vertices is not None):
                participle = "accessing vertices"
                for i in range(0,int(len(self.vertices)/self.vertex_depth)):
                    for axisIndex in range(0,3):
                        participle = "accessing vertex axis"
                        if (self.vertices[i*self.vertex_depth+axisIndex]<0):
                            participle = "accessing totals"
                            totals[axisIndex] += self.vertices[i*self.vertex_depth+axisIndex]
                            participle = "accessing vertex count"
                            counts[axisIndex] += 1
                        else:
                            participle = "accessing totals"
                            totals[axisIndex] += self.vertices[i*self.vertex_depth+axisIndex]
                            participle = "accessing vertex count"
                            counts[axisIndex] += 1
            for axisIndex in range(0,3):
                participle = "accessing final counts"
                if (counts[axisIndex]>0):
                    participle = "calculating results"
                    results[axisIndex] = totals[axisIndex] / counts[axisIndex]
        except Exception as e:
            print("Could not finish "+participle+" in get_center_average_of_vertices: "+str(e))
        return results[0], results[1], results[2]
    
    def set_textures_from_mtl_dict(self, mtl_dict):
        self.diffuse_color = mtl_dict.get('Kd') or self.diffuse_color
        self.diffuse_color = [float(v) for v in self.diffuse_color]
        self.ambient_color = mtl_dict.get('Ka') or self.ambient_color
        self.ambient_color = [float(v) for v in self.ambient_color]
        self.specular_color = mtl_dict.get('Ks') or self.specular_color
        self.specular_color = [float(v) for v in self.specular_color]
        self.specular_coefficent = float(mtl_dict.get('Ns', self.specular_coefficent))
        transparency = mtl_dict.get('d')
        if not transparency:
            transparency = 1.0 - float(mtl_dict.get('Tr', 0))
        self.transparency = float(transparency)

    def calculate_normals(self):
        #this does not work. The call to calculate_normals is even commented out at <https://github.com/kivy/kivy/blob/master/examples/3Drendering/objloader.py> 20 Mar 2014. 16 Apr 2015. 
        for i in range(int(len(self.indices) / (3))):
            fi = i * 3
            v1i = self.indices[fi]
            v2i = self.indices[fi + 1]
            v3i = self.indices[fi + 2]

            vs = self.vertices
            p1 = [vs[v1i + c] for c in range(3)]
            p2 = [vs[v2i + c] for c in range(3)]
            p3 = [vs[v3i + c] for c in range(3)]

            u,v  = [0,0,0], [0,0,0]
            for j in range(3):
                v[j] = p2[j] - p1[j]
                u[j] = p3[j] - p1[j]

            n = [0,0,0]
            n[0] = u[1] * v[2] - u[2] * v[1]
            n[1] = u[2] * v[0] - u[0] * v[2]
            n[2] = u[0] * v[1] - u[1] * v[0]

            for k in range(3):
                self.vertices[v1i + 3 + k] = n[k]
                self.vertices[v2i + 3 + k] = n[k]
                self.vertices[v3i + 3 + k] = n[k]   
    
    def dump(self, thisList, tabStringMinimum):
        thisList.append(tabStringMinimum+"object:")
        tabString="  "
        if self.name is not None:
            thisList.append(tabStringMinimum+tabString+"name: "+self.name)
        if self.objFileName is not None:
            thisList.append(tabStringMinimum+tabString+"objFileName: "+self.objFileName)
        for k,v in sorted(self.properties.items()):
            thisList.append(tabStringMinimum+tabString+k+": "+v)
            
        dumpAsYAMLArray(thisList, "_vertex_strings",self._vertex_strings,tabStringMinimum+tabString)
        thisTextureFileName=self.getTextureFileName()
        if thisTextureFileName is not None:
            thisList.append(tabStringMinimum+tabString+"getTextureFileName(): "+thisTextureFileName)
        dumpAsYAMLArray(thisList, "vertices",self.vertices,tabStringMinimum+tabString)
        dumpAsYAMLArray(thisList, "texcoords",self.texcoords,tabStringMinimum+tabString)
        dumpAsYAMLArray(thisList, "normals",self.normals,tabStringMinimum+tabString)
        dumpAsYAMLArray(thisList, "parameter_space_vertices",self.parameter_space_vertices,tabStringMinimum+tabString)
        dumpAsYAMLArray(thisList, "faces",self.faces,tabStringMinimum+tabString)


class PyMesher:
    
    meshes = None
    materials = None
    lastUntitledMeshNumber = -1
    lastCreatedMaterial = None
    lastCreatedMesh = None
    
    def theta_radians_from_rectangular(x, y):
        theta = 0.0
        if (y != 0.0) or (x != 0.0):
            # if x == 0:
            #     if y < 0:
            #         theta = math.radians(-90)
            #     elif y > 0:
            #         theta = math.radians(90.0)
            # elif y == 0:
            #     if x < 0:
            #         theta = math.radians(180.0)
            #     elif x > 0:
            #         theta = math.radians(0.0)
            # else:
            #     theta = math.atan(y/x)
            theta = math.atan2(y, x)
        return theta
    
    def dump(self, thisList):
        tabString="  "
        thisList.append("Objects:")
        for i in range(0,len(self.meshes)):
            self.meshes[i].dump(thisList, tabString)
        thisList.append("Materials:")
        for i in range(0,len(self.materials)):
            self.materials[i].dump(thisList, tabString)
            
    
    def __init__(self):
        self.meshes = []
        self.materials = []
        
    def createMesh(self):
        return PyMesherMesh()

    def createMaterial(self):
        return PyMesherMaterial()
    
    def getMeshByName(self, name):
        result = None
        if name is not None:
            if len(self.meshes)>0:
                for index in range(0,len(self.meshes)):
                    if name==self.meshes[index].name:
                        result=self.meshes[index]
        return result
        
    def load_obj(self,objFileName, swapyz=False):
        participle = "(before initializing)"
        linePlus1 = 1
        firstMeshIndex = len(self.meshes)
        try:
            self.lastCreatedMesh = None
            if os.path.exists(objFileName):
                for line in open(objFileName, "r"):
                    participle="before processing"
                    if line.startswith('#') and not line.startswith("# object "):
                        participle="skipping comment"
                    else:
                        participle="splitting"
                        values = line.split()
                        param = ""
                        participle="done splitting"
                        if len(values)>1:
                            participle="getting param"
                            param = line[len(values[0]):].strip()
                        if (values!=None) and (values != []):
                            if values[0] == 'o' or line.startswith("# object "):
                                self.lastCreatedMesh = self.createMesh()
                                self.lastCreatedMesh.objFileName = objFileName
                                if line.startswith("# object "):
                                    participle="parsing comment-style object statement"
                                    self.lastCreatedMesh.name = values[2]
                                else:
                                    participle="parsing 'o' statement"
                                    self.lastCreatedMesh.name = values[1]
                                self.meshes.append(self.lastCreatedMesh)
                            elif values[0] == 'mtllib':
                                participle = "calling _loadMtl"
                                self._loadMtl(resource_find(param))
                            else:
                                participle = "starting to parse property"
                                if self.lastCreatedMesh is None:
                                    untitledPrefixString = "untitled."
                                    self.lastUntitledMeshNumber += 1
                                    self.lastCreatedMesh = self.createMesh()
                                    self.lastCreatedMesh.objFileName = objFileName
                                    while self.getMeshByName(untitledPrefixString+str(self.lastUntitledMeshNumber)) is not None:
                                        self.lastUntitledMeshNumber += 1
                                        
                                    self.lastCreatedMesh.name = untitledPrefixString+str(self.lastUntitledMeshNumber)
                                    print("Warning: mesh data on line "+str(linePlus1)+" was not preceded by an 'o ' or '# object ' statement (default name:"+self.lastCreatedMesh.name+").")
                                if self.lastCreatedMesh is not None:
                                    if values[0] == 'v':
                                        participle="adding vertex"
                                        self.lastCreatedMesh._vertex_strings.append(values[1:])
                                        v = list(map(float, values[1:4]))
                                        if swapyz:
                                            v = v[0], v[2], v[1]
                                        self.lastCreatedMesh._obj_cache_vertices.append(v)
                                    elif values[0] == 'vt':
                                        participle="adding a texcoord set"
                                        #self.lastCreatedMesh.texcoords.append(values[1:])
                                        self.lastCreatedMesh.texcoords.append(list(map(float, values[1:3])))
                                    elif values[0] == 'vn':
                                        participle="adding a normal"
                                        #self.lastCreatedMesh.normals.append(values[1:])
                                        v = list(map(float, values[1:4]))
                                        if swapyz:
                                            v = v[0], v[2], v[1]
                                        self.lastCreatedMesh.normals.append(v)
                                    elif values[0] == 'vp':
                                        participle="adding a parameter space vertex"
                                        self.lastCreatedMesh.parameter_space_vertices.append(values[1:])
                                    elif values[0] == 'f':
                                        participle="adding a face"
                                        face = []
                                        texcoords = []
                                        norms = []
                                        for v in values[1:]:
                                            w = v.split('/')
                                            face.append(int(w[0]))
                                            if len(w) >= 2 and len(w[1]) > 0:
                                                texcoords.append(int(w[1]))
                                            else:
                                                texcoords.append(-1)
                                            if len(w) >= 3 and len(w[2]) > 0:
                                                norms.append(int(w[2]))
                                            else:
                                                norms.append(-1)
                                        self.lastCreatedMesh.faces.append((face, norms, texcoords)) #TODO: why was self.obj_material (formerly material) appended to this tuple in kivy-trackball version??
                                    else:
                                        self.lastCreatedMesh.properties[values[0]] = values[1]
                                else:
                                    raise ValueError("("+objFileName+") line "+str(linePlus1)+": Error--obj data wasn't preceded by an 'o' statement")
                    
                    linePlus1+=1
                    participle = "after processing"
            else:
                participle = "showing missing object file error"
                errorFilename=""
                if objFileName is not None:
                    errorFilename=objFileName
                print("ERROR in OBJ init: OBJ file \""+errorFilename+"\" not found")
            participle = "finalizing objects"
            for i in range(firstMeshIndex,len(self.meshes)):
                participle = "finalizing object index "+str(i)+" (Count:"+str(len(self.meshes))+")"
                self._finalize_obj_data(i)
        except Exception as e:
            print("Could not finish a mesh in load_obj while "+participle+" on line "+str(linePlus1)+": "+str(e))
            
    
    def _getMaterial(self, materialObjectName):
        result = None
        for i in range(0,len(self.materials)):
            if self.materials[i].name == materialObjectName:
                result = self.materials[i]
                break
        return result
            
    def _finalize_obj_data(self, index):
        participle = "(before initializing)"
        vertices_offset = None
        normals_offset = None
        texcoords_offset = None
        vertex_depth = 8
        #based on finish_object
#         if self._current_object == None:
#             return
# 
#         mesh = MeshData()
        participle="accessing object from list"
        thisObject = self.meshes[index]
        meshName = ""
        try:
            if thisObject.name is not None:
                meshName = thisObject.name
        except:
            pass  #don't care
        
        try:
            if thisObject.material is None:
                participle="processing material"
                if thisObject.properties["usemtl"] is not None:
                    thisObject.material=self._getMaterial(thisObject.properties["usemtl"])
                    if thisObject.material is not None:
                        thisObject.set_textures_from_mtl_dict(thisObject.material.properties)
        except Exception as e:
            print("Could not finish "+participle+" in _finalize_obj_data: "+str(e))
            
        raw_vertices = thisObject._obj_cache_vertices
        if thisObject.vertices is None:
            thisObject.vertices = []
            index = 0

            #obj format stores faces like (quads are allowed such as in following example):
            #f 1399/1619 1373/1593 1376/1596 1400/1620
            #format is:
            #f VERTEX_I VERTEX_I VERTEX_I VERTEX_I
            #or
            #f VERTEX_I/TEXCOORDSINDEX VERTEX_I/TEXCOORDSINDEX VERTEX_I/TEXCOORDSINDEX VERTEX_I/TEXCOORDSINDEX
            #or
            #f VERTEX_I/TEXCOORDSINDEX/NORMALINDEX VERTEX_I/TEXCOORDSINDEX/NORMALINDEX VERTEX_I/TEXCOORDSINDEX/NORMALINDEX VERTEX_I/TEXCOORDSINDEX/NORMALINDEX
            #where I is the index
            #FACE_VERTEX_COMPONENT_VERTEX_INDEX = 0
            #FACE_VERTEX_COMPONENT_TEXCOORDS_INDEX = 1
            #FACE_VERTEX_COMPONENT_NORMAL_INDEX = 2
            #NOTE: in obj format, TEXCOORDS_INDEX is optional unless NORMAL_INDEX is present
            #nskrypnik put them in a different order than obj format (0,1,2) for some reason so do this order instead:
            FACE_VERTEX_COMPONENT_VERTEX_INDEX = 0
            FACE_VERTEX_COMPONENT_TEXCOORDS_INDEX = 2
            FACE_VERTEX_COMPONENT_NORMAL_INDEX = 1
            
            try:
                if (len(thisObject.indices)<1):
                    participle = "before detecting vertex component offsets"
                    #detecting vertex component offsets is required since indices in an obj file are sometimes relative to the first index in the FILE not the object 
                    idx = 0
                    if thisObject.faces is not None:
                        #get offset
                        for faceIndex in range(0,len(thisObject.faces)):
                            for componentIndex in range(0,len(thisObject.faces[faceIndex])):
                                #print("found face "+str(faceIndex)+" component "+str(componentIndex)+": "+str(thisObject.faces[faceIndex][componentIndex]))
                                #print(str(thisObject.faces[faceIndex][vertexIndex]))
                                #if (len(thisObject.faces[faceIndex][componentIndex])>=FACE_VERTEX_COMPONENT_VERTEX_INDEX):
                                for vertexIndex in range(0,len(thisObject.faces[faceIndex][componentIndex])):
                                    if componentIndex==FACE_VERTEX_COMPONENT_VERTEX_INDEX:
                                        thisVertexIndex = thisObject.faces[faceIndex][componentIndex][vertexIndex]
                                        if vertices_offset is None or thisVertexIndex<vertices_offset:
                                            vertices_offset = thisVertexIndex
                                    #if (len(thisObject.faces[faceIndex][componentIndex])>=FACE_VERTEX_COMPONENT_TEXCOORDS_INDEX):
                                    elif componentIndex==FACE_VERTEX_COMPONENT_TEXCOORDS_INDEX:
                                        thisTexCoordIndex = thisObject.faces[faceIndex][componentIndex][vertexIndex]
                                        if texcoords_offset is None or thisTexCoordIndex<texcoords_offset:
                                            texcoords_offset = thisTexCoordIndex
                                    #if (len(thisObject.faces[faceIndex][componentIndex])>=FACE_VERTEX_COMPONENT_NORMAL_INDEX):
                                    elif componentIndex==FACE_VERTEX_COMPONENT_NORMAL_INDEX:
                                        thisNormalIndex = thisObject.faces[faceIndex][componentIndex][vertexIndex]
                                        if normals_offset is None or thisNormalIndex<normals_offset:
                                            normals_offset = thisNormalIndex
                                    
                        #if vertices_offset is not None:
                            #print("detected vertices_offset:"+str(vertices_offset))
                        #if texcoords_offset is not None:
                            #print("detected texcoords_offset:"+str(texcoords_offset))
                        #if normals_offset is not None:
                            #print("detected normals_offset:"+str(normals_offset))
                    
                    participle = "before processing faces"
                    
                    for f in thisObject.faces:
                        participle = "getting face components"
                        verts =  f[0]
                        norms = f[1]
                        tcs = f[2]
                        for i in range(3):
                            participle = "getting normal components"
                            #get normal components
                            n = (0.0, 0.0, 0.0)
                            if normals_offset is None:
                                normals_offset = 1
                            try:
                                participle = "getting normal components at "+str(norms[i]-normals_offset)
                                if norms[i] != -1:
                                    n = thisObject.normals[norms[i]-normals_offset]
                            except Exception as e:
                                print("Could not finish "+participle+" for mesh named '"+meshName+"'")
                            participle = "getting texture coordinate components"
                            participle = "getting texture coordinate components at "+str(i)
                            participle = "getting texture coordinate components using index "+str(tcs[i])
                            #get texture coordinate components
                            t = (0.0, 0.0)
                            if texcoords_offset is None:
                                texcoords_offset = 1
                            try:
                                if thisObject.texcoords is not None:
                                    participle = "getting normal components at "+str(tcs[i]-texcoords_offset)
                                    if tcs[i] != -1:
                                        participle = "using texture coordinates at index "+str(tcs[i]-texcoords_offset)+" (after applying texcoords_offset:"+str(texcoords_offset)+"; Count:"+str(len(thisObject.texcoords))+")"
                                        t = thisObject.texcoords[tcs[i]-texcoords_offset]
                                else:
                                    print("Warning: no texcoords found in mesh named '"+meshName+"'")
                            except Exception as e:
                                print("Could not finish "+participle+" for mesh named '"+meshName+"'")
            
                            participle = "getting vertex components"
                            if vertices_offset is None:
                                vertices_offset = 1
                            participle = "accessing face vertex "+str(verts[i]-vertices_offset)+" (after applying vertices_offset:"+str(vertices_offset)+"; Count:"+str(len(raw_vertices))+")"
                            try:
                                v = raw_vertices[verts[i]-vertices_offset]
                            except Exception as e:
                                print("Could not finish "+participle+" for mesh named '"+meshName+"'")
            
                            participle = "combining components"
                            data = [v[0], v[1], v[2], n[0], n[1], n[2], t[0], 1 - t[1]] #TODO: why does kivy-rotation3d version have t[1] instead of 1 - t[1] ????
                            thisObject.vertices.extend(data)
                        participle = "combining triangle indices"
                        tri = [idx, idx+1, idx+2]
                        thisObject.indices.extend(tri)
                        idx += 3
                        index += 1
                    participle = "generating pivot point"
                    thisObject.transform_pivot_to_geometry() 
            except Exception as e:
                print("Could not finish "+participle+" at face index "+str(index)+" in _finalize_obj_data: "+str(e))
            
                    #print("vertices after extending: "+str(thisObject.vertices))
                    #print("indices after extending: "+str(thisObject.indices))
        #         if thisObject.mtl is not None:
        #             thisObject.material = thisObject.mtl.get(thisObject.obj_material)
        #         if thisObject.material is not None and thisObject.material:
        #             thisObject.set_textures_from_mtl_dict(thisObject.material)
                #self.meshes[self._current_object] = mesh
                #mesh.calculate_normals()
                #self.faces = []
                
        #         if (len(thisObject.normals)<1):
        #             thisObject.calculate_normals()  #this does not work. The call to calculate_normals is even commented out at <https://github.com/kivy/kivy/blob/master/examples/3Drendering/objloader.py> 20 Mar 2014. 16 Apr 2015.
        else:
            print("Warning: already finalized obj data for mesh named '"+meshName+"'")
    #end def _finalize_obj_data
    
    
    def _loadMtl(self, mtlFileName):
        try:
            self.lastCreatedMaterial = None
            linePlus1 = 1
            if os.path.exists(mtlFileName):
                for line in open(mtlFileName, "r"):
                    if line.startswith('#'):
                        pass
                    else:
                        values = line.split()
                        if (values!=None) and (values != []):
                            if values[0] == 'newmtl':
                                self.lastCreatedMaterial = self.createMaterial()
                                self.lastCreatedMaterial.mtlFileName = mtlFileName
                                self.lastCreatedMaterial.name = values[1]
                                self.materials.append(self.lastCreatedMaterial)
                            else:
                                if self.lastCreatedMaterial is not None:
                                    if len(values)==2:
                                        self.lastCreatedMaterial.properties[values[0]] = values[1]
                                    else:
                                        self.lastCreatedMaterial.properties[values[0]] = values[1:]
                                else:
                                    raise ValueError("mtl data on line "+str(linePlus1)+" wasn't preceded by newmtl statement")
                    linePlus1+=1
                    
            else:
                errorFilename=""
                if mtlFileName is not None:
                    errorFilename=mtlFileName
                print("ERROR in MTL init: MTL file \""+errorFilename+"\" not found")
        except Exception as e:
            print("Could not finish a material in loadMtl: "+str(e))
        
        



ILLUMINATIONMODEL_DESCRIPTION_STRINGS = ["Color on and Ambient off","Color on and Ambient on","Highlight on","Reflection on and Ray trace on","Transparency: Glass on, Reflection: Ray trace on","Reflection: Fresnel on and Ray trace on","Transparency: Refraction on, Reflection: Fresnel off and Ray trace on","Transparency: Refraction on, Reflection: Fresnel on and Ray trace on","Reflection on and Ray trace off","Transparency: Glass on, Reflection: Ray trace off","Casts shadows onto invisible surfaces"]

def getIlluminationModelDescription(self, illuminationModelIndex):
    global ILLUMINATIONMODEL_DESCRIPTION_STRINGS
    resultString = None
    if (illuminationModelIndex>=0) and (illuminationModelIndex<len(ILLUMINATIONMODEL_DESCRIPTION_STRINGS)):
        ILLUMINATIONMODEL_DESCRIPTION_STRINGS[illuminationModelIndex]
    return resultString

