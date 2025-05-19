from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_GET
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.middleware.csrf import get_token
from .executor import execute_code
import json
import os
from datetime import datetime
import shutil
import tempfile
import subprocess
import traceback
import logging
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from django.views.decorators.http import require_GET
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

# Set up logging
logger = logging.getLogger(__name__)

# Create your views here.

@ensure_csrf_cookie
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
        projects_dir = os.path.join(os.getcwd(), 'projects')
        if not os.path.exists(projects_dir):
            os.makedirs(projects_dir, exist_ok=True)
            
        projects = []
        for project_name in os.listdir(projects_dir):
            project_dir = os.path.join(projects_dir, project_name)
            if os.path.isdir(project_dir):
                # Get creation time
                created_at = datetime.fromtimestamp(os.path.getctime(project_dir))
                projects.append({
                    'id': project_name,
                    'name': project_name,
                    'created_at': created_at.isoformat()
                })
                
        return JsonResponse({'projects': projects})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def build_file_tree(base_path, rel_path=""):
    abs_path = os.path.join(base_path, rel_path)
    items = []
    for entry in sorted(os.listdir(abs_path)):
        entry_path = os.path.join(abs_path, entry)
        rel_entry_path = os.path.join(rel_path, entry) if rel_path else entry
        if os.path.isdir(entry_path):
            items.append({
                "id": f"{rel_entry_path.replace(os.sep, '/')}",
                "name": entry,
                "is_folder": True,
                "children": build_file_tree(base_path, rel_entry_path)
            })
        else:
            items.append({
                "id": f"{rel_entry_path.replace(os.sep, '/')}",
                "name": entry,
                "is_folder": False
            })
    return items

@require_http_methods(["GET"])
def list_project_files(request, project_id):
    try:
        base_dir = os.path.abspath(os.getcwd())
        projects_dir = os.path.normpath(os.path.join(base_dir, 'projects'))
        project_dir = os.path.normpath(os.path.join(projects_dir, project_id))
        if not os.path.exists(project_dir):
            return json_response({'error': 'Project not found'}, status=404)
        files = build_file_tree(project_dir)
        return json_response({"files": files})
    except Exception as e:
        logger.error(f"Error listing project files: {str(e)}")
        return json_response({'error': str(e)}, status=500)

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
            'id': f"{project_id}/{rel_path}",  # Include project_id in the file ID
            'name': file_name,
            'path': rel_path,
            'is_folder': is_folder
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def json_response(data, status=200):
    """Standardized JSON response helper"""
    try:
        return JsonResponse(data, status=status, encoder=DjangoJSONEncoder)
    except Exception as e:
        logger.error(f"Error creating JSON response: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def json_error_response(error_message, status=500):
    """Helper function to return JSON error responses"""
    logger.error(f"Returning JSON error response: {error_message} (status: {status})")
    return json_response({'error': error_message}, status=status)

@require_GET
def get_file_content(request, file_id):
    """
    Get the content of a file.
    The file_id should be in the format: project_id/file_path
    """
    try:
        # Basic validation
        if not file_id:
            logger.error("File ID is missing")
            return json_response({'error': 'File ID is required'}, status=400)

        # Log the incoming request
        logger.debug(f"Received request for file_id: {file_id}")
        logger.debug(f"Request headers: {dict(request.headers)}")

        # Split file_id into project_id and file_path
        try:
            project_id, file_path = file_id.split('/', 1)
            logger.debug(f"Split file_id: project_id={project_id}, file_path={file_path}")
        except ValueError:
            logger.error(f"Invalid file_id format: {file_id}")
            return json_response({'error': 'Invalid file ID format'}, status=400)

        # Validate project_id and file_path
        if not project_id or not file_path:
            logger.error(f"Invalid project_id or file_path: project_id={project_id}, file_path={file_path}")
            return json_response({'error': 'Invalid project ID or file path'}, status=400)

        # Normalize paths
        try:
            # Get the absolute path to the projects directory
            base_dir = os.path.abspath(os.getcwd())
            projects_dir = os.path.normpath(os.path.join(base_dir, 'projects'))
            
            # Ensure the projects directory exists
            if not os.path.exists(projects_dir):
                logger.info(f"Creating projects directory: {projects_dir}")
                os.makedirs(projects_dir)
            
            # Construct and normalize the project directory path
            project_dir = os.path.normpath(os.path.join(projects_dir, project_id))
            
            # Construct and normalize the full file path
            full_path = os.path.normpath(os.path.join(project_dir, file_path))
            
            # Log the paths for debugging
            logger.debug(f"Base directory: {base_dir}")
            logger.debug(f"Projects directory: {projects_dir}")
            logger.debug(f"Project directory: {project_dir}")
            logger.debug(f"Full file path: {full_path}")
            
            # Security check: ensure the file is within the projects directory
            if not full_path.startswith(projects_dir):
                logger.error(f"Security check failed: {full_path} is not within {projects_dir}")
                return json_response({'error': 'Invalid file path'}, status=400)
            
            # Check if project exists
            if not os.path.exists(project_dir):
                logger.error(f"Project directory not found: {project_dir}")
                return json_response({'error': 'Project not found'}, status=404)
            
            # Check if file exists
            if not os.path.exists(full_path):
                logger.error(f"File not found: {full_path}")
                return json_response({'error': 'File not found'}, status=404)
            
            # Check if path is a directory
            if os.path.isdir(full_path):
                logger.error(f"Path is a directory: {full_path}")
                return json_response({'error': 'Cannot get content of a directory'}, status=400)
            
            # Read file content
            try:
                # First try to read with UTF-8
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    logger.debug(f"Successfully read file: {full_path} with UTF-8 encoding")
                except UnicodeDecodeError:
                    # If UTF-8 fails, try with binary mode and decode
                    with open(full_path, 'rb') as f:
                        content = f.read().decode('utf-8', errors='replace')
                    logger.debug(f"Successfully read file: {full_path} with binary mode and UTF-8 decode")
            except PermissionError:
                logger.error(f"Permission denied reading file: {full_path}")
                return json_response({'error': 'Permission denied'}, status=403)
            except Exception as e:
                logger.error(f"Error reading file {full_path}: {str(e)}")
                return json_response({'error': f'Error reading file: {str(e)}'}, status=500)
            
            # Return file data
            response_data = {
                'id': file_id,
                'name': os.path.basename(file_path),
                'path': file_path,
                'content': content
            }
            
            # Log the response data for debugging
            logger.debug(f"Returning file data: {response_data}")
            
            return json_response(response_data)
            
        except Exception as e:
            logger.error(f"Error processing file path for {file_id}: {str(e)}")
            return json_response({'error': f'Error processing file path: {str(e)}'}, status=500)
            
    except Exception as e:
        logger.error(f"Unexpected error in get_file_content for {file_id}: {str(e)}")
        return json_response({'error': f'Unexpected error: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def save_file(request, file_id):
    try:
        # Extract project_id and file_path from file_id
        parts = file_id.split('/', 1)
        if len(parts) != 2:
            return json_response({'error': 'Invalid file ID format'}, status=400)
            
        project_id, file_path = parts
        
        try:
            data = json.loads(request.body)
            content = data.get('content', '')
        except json.JSONDecodeError:
            return json_response({'error': 'Invalid JSON data'}, status=400)

        # Normalize paths
        try:
            base_dir = os.path.abspath(os.getcwd())
            projects_dir = os.path.normpath(os.path.join(base_dir, 'projects'))
            project_dir = os.path.normpath(os.path.join(projects_dir, project_id))
            full_path = os.path.normpath(os.path.join(project_dir, file_path))
            
            # Security check: ensure the file is within the projects directory
            if not full_path.startswith(projects_dir):
                logger.error(f"Security check failed: {full_path} is not within {projects_dir}")
                return json_response({'error': 'Invalid file path'}, status=400)
            
            # Ensure project directory exists
            if not os.path.exists(project_dir):
                logger.error(f"Project directory not found: {project_dir}")
                return json_response({'error': 'Project not found'}, status=404)
            
            # Ensure parent directory exists
            parent_dir = os.path.dirname(full_path)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            
            logger.debug(f"Full file path: {full_path}")
        except Exception as e:
            logger.error(f"Error processing file path: {str(e)}")
            return json_response({'error': 'Error processing file path'}, status=500)

        # Validate file is not a directory
        if os.path.exists(full_path) and os.path.isdir(full_path):
            logger.error(f"Path is a directory: {full_path}")
            return json_response({'error': 'Cannot save content to a directory'}, status=400)

        # Write content to file
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.debug(f"Successfully saved file: {full_path}")
            return json_response({
                'success': True,
                'message': 'File saved successfully',
                'file': {
                    'id': file_id,
                    'name': os.path.basename(file_path),
                    'path': file_path
                }
            })
        except PermissionError:
            logger.error(f"Permission denied writing to file: {full_path}")
            return json_response({'error': 'Permission denied'}, status=403)
        except Exception as e:
            logger.error(f"Error writing to file {full_path}: {str(e)}")
            return json_response({'error': f'Error writing to file: {str(e)}'}, status=500)

    except Exception as e:
        logger.error(f"Unexpected error in save_file for {file_id}: {str(e)}")
        return json_response({'error': f'Unexpected error: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def delete_file(request, file_id):
    try:
        # Extract project_id and file_path from file_id
        parts = file_id.split('/', 1)
        if len(parts) != 2:
            return json_response({'error': 'Invalid file ID format'}, status=400)
            
        project_id, file_path = parts
        projects_dir = os.path.join(os.getcwd(), 'projects')
        full_path = os.path.join(projects_dir, project_id, file_path)
        
        if not os.path.exists(full_path):
            return json_response({'error': 'File not found'}, status=404)
            
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
            
        return json_response({
            'success': True,
            'message': 'File deleted successfully',
            'file': {
                'id': file_id,
                'name': os.path.basename(file_path),
                'path': file_path
            }
        })
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {str(e)}")
        return json_response({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def rename_file(request, file_id):
    try:
        # Extract project_id and file_path from file_id
        parts = file_id.split('/', 1)
        if len(parts) != 2:
            return json_response({'error': 'Invalid file ID format'}, status=400)
            
        project_id, file_path = parts
        
        try:
            data = json.loads(request.body)
            new_name = data.get('new_name')
        except json.JSONDecodeError:
            return json_response({'error': 'Invalid JSON data'}, status=400)
        
        if not new_name:
            return json_response({'error': 'New name is required'}, status=400)
            
        projects_dir = os.path.join(os.getcwd(), 'projects')
        old_path = os.path.join(projects_dir, project_id, file_path)
        
        if not os.path.exists(old_path):
            return json_response({'error': 'File not found'}, status=404)
            
        # Get the directory containing the file
        dir_path = os.path.dirname(old_path)
        new_path = os.path.join(dir_path, new_name)
        
        if os.path.exists(new_path):
            return json_response({'error': 'A file with this name already exists'}, status=400)
            
        os.rename(old_path, new_path)
        
        # Calculate new relative path
        new_rel_path = os.path.relpath(new_path, os.path.join(projects_dir, project_id))
        new_file_id = f"{project_id}/{new_rel_path}"
        
        return json_response({
            'success': True,
            'message': 'File renamed successfully',
            'file': {
                'id': new_file_id,
                'name': new_name,
                'path': new_rel_path,
                'is_folder': os.path.isdir(new_path)
            }
        })
    except Exception as e:
        logger.error(f"Error renaming file {file_id}: {str(e)}")
        return json_response({'error': str(e)}, status=500)

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
            
        # Create a temporary directory for execution
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write code to a temporary file
            file_ext = {
                'python': '.py',
                'javascript': '.js',
                'java': '.java',
                'cpp': '.cpp',
                'c': '.c',
                'php': '.php',
                'ruby': '.rb',
                'go': '.go',
                'rust': '.rs',
                'swift': '.swift',
                'kotlin': '.kt',
                'typescript': '.ts'
            }.get(language, '.txt')
            
            temp_file = os.path.join(temp_dir, f'temp{file_ext}')
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
                
            # Execute the code based on language
            try:
                if language == 'python':
                    result = subprocess.run(['python', temp_file], 
                                         capture_output=True, 
                                         text=True, 
                                         timeout=10)
                elif language == 'javascript':
                    result = subprocess.run(['node', temp_file], 
                                         capture_output=True, 
                                         text=True, 
                                         timeout=10)
                else:
                    return JsonResponse({'error': f'Unsupported language: {language}'}, status=400)
                    
                if result.returncode == 0:
                    return JsonResponse({'output': result.stdout})
                else:
                    return JsonResponse({'error': result.stderr})
                    
            except subprocess.TimeoutExpired:
                return JsonResponse({'error': 'Code execution timed out'}, status=408)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
                
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def delete_project(request, project_id):
    try:
        # Get the absolute path to the projects directory
        base_dir = os.path.abspath(os.getcwd())
        projects_dir = os.path.normpath(os.path.join(base_dir, 'projects'))
        project_dir = os.path.normpath(os.path.join(projects_dir, project_id))
        
        # Security check: ensure the project is within the projects directory
        if not project_dir.startswith(projects_dir):
            return json_response({'error': 'Invalid project path'}, status=400)
        
        # Check if project exists
        if not os.path.exists(project_dir):
            return json_response({'error': 'Project not found'}, status=404)
        
        # Delete the project directory and all its contents
        shutil.rmtree(project_dir)
        
        return json_response({'success': True, 'message': 'Project deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {str(e)}")
        return json_response({'error': f'Error deleting project: {str(e)}'}, status=500)
