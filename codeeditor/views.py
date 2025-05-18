from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .executor import execute_code
import json
import os
from datetime import datetime
import shutil

# Create your views here.

def editor(request):
    return render(request, 'editor.html')

@csrf_exempt
@require_http_methods(["POST"])
def create_project(request):
    try:
        data = json.loads(request.body)
        project_name = data.get('name')
        
        if not project_name:
            return JsonResponse({'error': 'Project name is required'}, status=400)
            
        # Create projects directory if it doesn't exist
        projects_dir = os.path.join(os.getcwd(), 'projects')
        os.makedirs(projects_dir, exist_ok=True)
            
        # Create project directory
        project_dir = os.path.join(projects_dir, project_name)
        if os.path.exists(project_dir):
            return JsonResponse({'error': 'Project already exists'}, status=400)
            
        os.makedirs(project_dir, exist_ok=True)
        
        # Create project metadata
        project_data = {
            'id': project_name,  # Use project name as ID for easier file handling
            'name': project_name,
            'created_at': datetime.now().isoformat()
        }
        
        return JsonResponse(project_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def list_projects(request):
    try:
        projects = []
        projects_dir = os.path.join(os.getcwd(), 'projects')
        
        if os.path.exists(projects_dir):
            for project_name in os.listdir(projects_dir):
                project_path = os.path.join(projects_dir, project_name)
                if os.path.isdir(project_path):
                    created_at = datetime.fromtimestamp(os.path.getctime(project_path))
                    projects.append({
                        'id': project_name,  # Use project name as ID
                        'name': project_name,
                        'created_at': created_at.isoformat()
                    })
        
        return JsonResponse({'projects': projects})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def list_project_files(request, project_id):
    try:
        projects_dir = os.path.join(os.getcwd(), 'projects')
        project_dir = os.path.join(projects_dir, project_id)
        
        if not os.path.exists(project_dir):
            return JsonResponse({'error': 'Project not found'}, status=404)
            
        files = []
        for root, dirs, filenames in os.walk(project_dir):
            for dirname in dirs:
                dir_path = os.path.join(root, dirname)
                rel_path = os.path.relpath(dir_path, project_dir)
                files.append({
                    'id': rel_path,  # Use relative path as ID
                    'name': dirname,
                    'path': rel_path,
                    'is_folder': True,
                    'children': []
                })
                
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, project_dir)
                files.append({
                    'id': rel_path,  # Use relative path as ID
                    'name': filename,
                    'path': rel_path,
                    'is_folder': False
                })
                
        return JsonResponse({'files': files})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_file(request, project_id):
    try:
        data = json.loads(request.body)
        file_name = data.get('name')
        is_folder = data.get('is_folder', False)
        parent_path = data.get('parent_path', '')
        
        if not file_name:
            return JsonResponse({'error': 'File name is required'}, status=400)
            
        projects_dir = os.path.join(os.getcwd(), 'projects')
        project_dir = os.path.join(projects_dir, project_id)
        
        if not os.path.exists(project_dir):
            return JsonResponse({'error': 'Project not found'}, status=404)
            
        # Create full path including parent directory if specified
        file_path = os.path.join(project_dir, parent_path, file_name)
        if os.path.exists(file_path):
            return JsonResponse({'error': 'File already exists'}, status=400)
            
        if is_folder:
            os.makedirs(file_path, exist_ok=True)
        else:
            with open(file_path, 'w') as f:
                f.write('')
                
        rel_path = os.path.relpath(file_path, project_dir)
        return JsonResponse({
            'id': rel_path,
            'name': file_name,
            'path': rel_path,
            'is_folder': is_folder
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_file_content(request, file_id):
    try:
        # Extract project_id and file_path from file_id
        parts = file_id.split('/', 1)
        if len(parts) != 2:
            return JsonResponse({'error': 'Invalid file ID'}, status=400)
            
        project_id, file_path = parts
        projects_dir = os.path.join(os.getcwd(), 'projects')
        full_path = os.path.join(projects_dir, project_id, file_path)
        
        if not os.path.exists(full_path):
            return JsonResponse({'error': 'File not found'}, status=404)
            
        if os.path.isdir(full_path):
            return JsonResponse({'error': 'Cannot get content of a directory'}, status=400)
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return JsonResponse({
            'id': file_id,
            'content': content
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def save_file(request, file_id):
    try:
        # Extract project_id and file_path from file_id
        parts = file_id.split('/', 1)
        if len(parts) != 2:
            return JsonResponse({'error': 'Invalid file ID'}, status=400)
            
        project_id, file_path = parts
        data = json.loads(request.body)
        content = data.get('content', '')
        
        projects_dir = os.path.join(os.getcwd(), 'projects')
        full_path = os.path.join(projects_dir, project_id, file_path)
        
        if not os.path.exists(full_path):
            return JsonResponse({'error': 'File not found'}, status=404)
            
        if os.path.isdir(full_path):
            return JsonResponse({'error': 'Cannot save content to a directory'}, status=400)
            
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def delete_file(request, file_id):
    try:
        # Extract project_id and file_path from file_id
        parts = file_id.split('/', 1)
        if len(parts) != 2:
            return JsonResponse({'error': 'Invalid file ID'}, status=400)
            
        project_id, file_path = parts
        projects_dir = os.path.join(os.getcwd(), 'projects')
        full_path = os.path.join(projects_dir, project_id, file_path)
        
        if not os.path.exists(full_path):
            return JsonResponse({'error': 'File not found'}, status=404)
            
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
            
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def rename_file(request, file_id):
    try:
        # Extract project_id and file_path from file_id
        parts = file_id.split('/', 1)
        if len(parts) != 2:
            return JsonResponse({'error': 'Invalid file ID'}, status=400)
            
        project_id, file_path = parts
        data = json.loads(request.body)
        new_name = data.get('new_name')
        
        if not new_name:
            return JsonResponse({'error': 'New name is required'}, status=400)
            
        projects_dir = os.path.join(os.getcwd(), 'projects')
        old_path = os.path.join(projects_dir, project_id, file_path)
        
        if not os.path.exists(old_path):
            return JsonResponse({'error': 'File not found'}, status=404)
            
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        if os.path.exists(new_path):
            return JsonResponse({'error': 'File already exists'}, status=400)
            
        os.rename(old_path, new_path)
        
        new_rel_path = os.path.relpath(new_path, os.path.join(projects_dir, project_id))
        return JsonResponse({
            'id': f"{project_id}/{new_rel_path}",
            'name': new_name
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def run_code(request):
    try:
        data = json.loads(request.body)
        code = data.get('code', '')
        language = data.get('language', 'python')
        filename = data.get('filename', '')
        
        if not code:
            return JsonResponse({'error': 'No code provided'}, status=400)
            
        output = execute_code(code, language, filename)
        return JsonResponse({'output': output})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
