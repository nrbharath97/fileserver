# from posix import ST_NOATIME
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
import requests
from rest_framework.decorators import action, api_view
from rest_framework import viewsets, status
from rest_framework.response import Response


from .models import Files
from .serializers import FilesSerializer

# class FilesViewSet(viewsets.ModelViewSet):
#     serializer_class = FilesSerializer
#     queryset = Files.objects.all()

#     @action(detail=True, methods=['DELETE'])
#     def delete(request):
#         print("Inside delete custom def")
#         file_to_be_deleted = request.GET.get('file_name','')
#         file_to_be_deleted = Files.objects.get(fs_file="uploads/" + file_to_be_deleted)
#         file_to_be_deleted.delete()
#         return HttpResponse({'message': 'File deleted'}, status=status.HTTP_204_NO_CONTENT, content_type='text/plain')

#     @action(detail=True, methods=['POST'])
#     def post(request):
#         print("Inside post custom def")
#         print(request)

        


# @api_view(['GET', 'POST', 'DELETE'])
# def files_list(request):
#     print("insdie getasdfdsf")
#     if request.method == 'GET':
#         files = Files.objects.all()
#         print("insdasdfasdfsdfie getasdfdsf")
        
#         serializer_class = FilesSerializer(files, many=True)
#         return JsonResponse(serializer_class.data, safe=False)


# @api_view(['GET', 'PUT', 'DELETE'])
# def files_detail(request, fs_file):
#     print(fs_file)
#     print("insdie delete with pk")    
#     try:
#         files = Files.objects.get(fs_file=fs_file)
#         print(files)
#         print('\n')
#         for i in files:
#             print(i.id)
#     except Files.DoesNotExist:
#         return JsonResponse({'message': 'File does not exist'}, status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'DELETE':
#         files.delete()
#         return JsonResponse({'message': 'File is deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
#     if request.method == 'GET':
#         print("insdie get")
#         file_names = Files.objects.all()
#         serializer_class = FilesSerializer(file_names, many=True)
#         return JsonResponse(serializer_class.data, safe=False)




# re-written code using class-based views from documention of DRF

from fileops.models import Files
from fileops.serializers import FilesSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from fileserver.settings import MEDIA_ROOT
import os
import collections


class FilesList(APIView):
    def get(self, request, format=None):
        print("Inside get custom def1")
        files = Files.objects.all()
        serializer = FilesSerializer(files, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        print("Inside post custom def1")
        serializer = FilesSerializer(data=request.data)

        filename_to_be_added = str(request.FILES['fs_file'])

        try:
            file_to_be_added = Files.objects.filter(fs_file="uploads/" + filename_to_be_added)
            print("search reuslt in try block")
        except:
            print("search reuslt in catch block")            
            file_to_be_added = None
            print("inside except block" , file_to_be_added)

        print(file_to_be_added)

        if file_to_be_added is None:
            return Response({'message': 'Something went wrong. Please try again'}, status=status.HTTP_400_BAD_REQUEST)

        if file_to_be_added.exists() == False:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({'message': 'File with the same name already exists!'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        print("Inside put custom def1")
        serializer = FilesSerializer(data=request.data)

        #Get content from user uploaded file
        filename_to_be_added = str(request.FILES['fs_file'])
        file_from_user = request.FILES['fs_file'].read()
        data = ""
        for char in file_from_user:
            data = data + chr(char)

        content_from_user_file = []
        content_from_user_file.append(data.split(" "))
        # print("Content from user file: " , content_from_user_file)

        #Get content from the file on the server
        filename_from_server = MEDIA_ROOT + '\\uploads\\' + filename_to_be_added
        print(filename_from_server)
        file_from_server = open(filename_from_server, 'r')
        content_from_server_file = []
        for i in file_from_server.readlines():
            content_from_server_file.append(i.strip().split(" "))
        # print("Content from server file: ", content_from_server_file)   
        file_from_server.close()


        #Check if file with same name exists 
        try:
            file_to_be_added = Files.objects.filter(fs_file="uploads/" + filename_to_be_added)
        #except catches any unexpected error encountered while running the above query
        except:
            file_to_be_added = None            

        #If unexpected error is encountered, then return the below message
        if file_to_be_added is None:
            return Response({'message': 'Something went wrong. Please try again'}, status=status.HTTP_400_BAD_REQUEST)

        #If file does not exist, then create a new file and add the content
        if file_to_be_added.exists() == False:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        #If file exists, compare the content inside each file; based on the result, update the file on the server or return a message that the file and the contents are same
        if content_from_user_file == content_from_server_file:
            return Response({'message': 'File with the same name and content already exists!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            file_to_be_deleted = Files.objects.get(fs_file="uploads/" + filename_to_be_added)
            file_to_be_deleted.delete()
            file_path = MEDIA_ROOT + '\\uploads\\' + filename_to_be_added
            os.remove(file_path) 
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)                           

    def delete(self, request, format=None):
        print("Inside delete custom def1")
        filename_to_be_deleted = request.GET.get('fs_file','')
        
        try:
            file_to_be_deleted = Files.objects.get(fs_file=filename_to_be_deleted)
        except:
            file_to_be_deleted = None
        
        try:
            file_to_be_deleted.delete()
            file_path = MEDIA_ROOT + '\\uploads\\' + filename_to_be_deleted
            os.remove(file_path)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return JsonResponse({'message': 'File cannot be deleted!'}, status=status.HTTP_400_BAD_REQUEST)


class FilesDetail(APIView):
    def get_object(self, pk):
        try:
            return Files.objects.get(pk=pk)
        except Files.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        print("Inside get custom def2")                
        files = self.get_object(pk)
        serializer = FilesSerializer(files)
        return Response(serializer.data)

    def put(self, request, pk, format=None):

        # 1. check if the file exists
        # 2. if does not exists, basically add the file similar to post operation
        # 3. If it exists, then compare the contents of both files (read op on files) and update content from user file to db file if data is not same
            # // File operations - path - use media root


        files = self.get_object(pk)
        serializer = FilesSerializer(files, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        print("Inside delete custom def2")
        files = self.get_object(pk)
        files.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class FilesWordCount(APIView):
    def get(self, request, format=None):
        print("Inside wc custom def1")
        files = Files.objects.all()
        content_from_file = []
        list_of_words = []
        for file in files:
            file_name = str(file.fs_file)
            file_name = file_name.split('uploads/')[1]
            file_path = MEDIA_ROOT + '\\uploads\\' + file_name

            # print(file_path)
            with open(file_path, 'r') as f:
                for i in f.readlines():
                    content_from_file.append(i.strip().split(" "))
                # print("Content from current file: ", content_from_file)

        for li in content_from_file:
            for sl in li:
                list_of_words.append(sl)

        return Response({'Total number of words in all the files is': len(list_of_words)}, status=status.HTTP_200_OK)

class FilesFreqWordCount(APIView):
    def get(self, request, format=None):
        print("Inside freq word custom def1")
        
        #Parsing the Params from request
        if request.GET.get('order',''):
            order_val = request.GET.get('order','')
        else:
            order_val = 'asc'

        print(order_val)

        #Get list of words in all files and store it into list_of_words array
        files = Files.objects.all()
        content_from_file = []
        list_of_words = []
        
        for file in files:
            file_name = str(file.fs_file)
            file_name = file_name.split('uploads/')[1]
            file_path = MEDIA_ROOT + '\\uploads\\' + file_name

            with open(file_path, 'r') as f:
                for i in f.readlines():
                    content_from_file.append(i.strip().split(" "))

        for li in content_from_file:
            for sl in li:
                list_of_words.append(sl)

        occurrences = collections.Counter(list_of_words)
        # print("Max occurences word: ")
        # print(max(occurrences, key=occurrences.get))

        fw=[]
        if order_val == 'dsc':
            fw = occurrences.most_common()[:-11:-1]

        else:
            fw = occurrences.most_common(10)

        return Response({'Here are the freq words from all the files: ': fw}, status=status.HTTP_200_OK)        