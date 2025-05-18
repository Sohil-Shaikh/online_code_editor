import subprocess
import tempfile
import os
import json
import sys
import traceback

def execute_code(code, language='python', filename=''):
    """
    Execute code in the specified language and return the output.
    
    Args:
        code (str): The code to execute
        language (str): The programming language (python, javascript, etc.)
        filename (str): The name of the file being executed
        
    Returns:
        str: The output of the code execution
    """
    try:
        # Create a temporary file with the appropriate extension
        ext = get_file_extension(language)
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
            temp_file.write(code.encode('utf-8'))
            temp_file.flush()
            
            # Execute the code based on the language
            if language == 'python':
                result = subprocess.run([sys.executable, temp_file.name],
                                     capture_output=True,
                                     text=True,
                                     timeout=10)
            elif language == 'javascript':
                result = subprocess.run(['node', temp_file.name],
                                     capture_output=True,
                                     text=True,
                                     timeout=10)
            else:
                return f"Unsupported language: {language}"
            
            # Clean up the temporary file
            os.unlink(temp_file.name)
            
            # Return the output or error
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
                
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except Exception as e:
        return f"Error: {str(e)}"

def get_file_extension(language):
    """
    Get the file extension for a given programming language.
    
    Args:
        language (str): The programming language
        
    Returns:
        str: The file extension
    """
    extensions = {
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
    }
    return extensions.get(language.lower(), '.txt')

def execute_python(code, filename=None):
    """
    Execute Python code and return the output
    """
    print("\n=== Python Execution Debug ===")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
        print(f"Created temporary file: {temp_file}")

    try:
        print(f"Running Python interpreter: {sys.executable}")
        result = subprocess.run([sys.executable, temp_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        print(f"Return code: {result.returncode}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        
        if result.returncode == 0:
            return {'output': result.stdout.strip()}
        else:
            return {'error': result.stderr.strip()}
    except subprocess.TimeoutExpired:
        print("Error: Code execution timed out")
        return {'error': 'Code execution timed out after 10 seconds'}
    except Exception as e:
        print(f"Error in execute_python: {str(e)}")
        print(traceback.format_exc())
        return {'error': f'Python execution error: {str(e)}'}
    finally:
        try:
            os.unlink(temp_file)
            print(f"Deleted temporary file: {temp_file}")
        except Exception as e:
            print(f"Error deleting temporary file: {str(e)}")

def execute_javascript(code, filename=None):
    """
    Execute JavaScript code and return the output
    """
    print("\n=== JavaScript Execution Debug ===")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(code)
        temp_file = f.name
        print(f"Created temporary file: {temp_file}")

    try:
        # Check if Node.js is installed
        try:
            node_version = subprocess.run(['node', '--version'], 
                                        capture_output=True, 
                                        text=True, 
                                        check=True)
            print(f"Node.js version: {node_version.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error: Node.js is not installed: {str(e)}")
            return {'error': 'Node.js is not installed on the server'}

        print(f"Running Node.js on file: {temp_file}")
        result = subprocess.run(['node', temp_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        print(f"Return code: {result.returncode}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        
        if result.returncode == 0:
            return {'output': result.stdout.strip()}
        else:
            return {'error': result.stderr.strip()}
    except subprocess.TimeoutExpired:
        print("Error: Code execution timed out")
        return {'error': 'Code execution timed out after 10 seconds'}
    except Exception as e:
        print(f"Error in execute_javascript: {str(e)}")
        print(traceback.format_exc())
        return {'error': f'JavaScript execution error: {str(e)}'}
    finally:
        try:
            os.unlink(temp_file)
            print(f"Deleted temporary file: {temp_file}")
        except Exception as e:
            print(f"Error deleting temporary file: {str(e)}")

def execute_java(code, filename=None):
    """
    Execute Java code and return the output
    """
    print("\n=== Java Execution Debug ===")
    
    # Create a temporary directory for Java files
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Check if Java is installed
            try:
                java_version = subprocess.run(['java', '-version'], 
                                           capture_output=True, 
                                           text=True)
                print(f"Java version: {java_version.stderr.split('\n')[0]}")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"Error: Java is not installed: {str(e)}")
                return {'error': 'Java is not installed on the server'}

            # Write the Java code to a file
            class_name = filename.split('.')[0] if filename else 'Main'
            java_file = os.path.join(temp_dir, f"{class_name}.java")
            with open(java_file, 'w') as f:
                f.write(code)
            print(f"Created Java file: {java_file}")

            # Compile the Java code
            compile_result = subprocess.run(['javac', java_file],
                                         capture_output=True,
                                         text=True,
                                         timeout=10)
            
            if compile_result.returncode != 0:
                return {'error': compile_result.stderr.strip()}

            # Run the compiled Java program
            run_result = subprocess.run(['java', '-cp', temp_dir, class_name],
                                      capture_output=True,
                                      text=True,
                                      timeout=10)
            
            if run_result.returncode == 0:
                return {'output': run_result.stdout.strip()}
            else:
                return {'error': run_result.stderr.strip()}
        except subprocess.TimeoutExpired:
            return {'error': 'Code execution timed out after 10 seconds'}
        except Exception as e:
            print(f"Error in execute_java: {str(e)}")
            print(traceback.format_exc())
            return {'error': f'Java execution error: {str(e)}'}

def execute_cpp(code, filename=None):
    """
    Execute C++ code and return the output
    """
    print("\n=== C++ Execution Debug ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Write the C++ code to a file
            cpp_file = os.path.join(temp_dir, 'main.cpp')
            with open(cpp_file, 'w') as f:
                f.write(code)
            print(f"Created C++ file: {cpp_file}")

            # Check if g++ is installed
            try:
                gpp_version = subprocess.run(['g++', '--version'], 
                                          capture_output=True, 
                                          text=True, 
                                          check=True)
                print(f"g++ version: {gpp_version.stdout.split('\n')[0]}")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"Error: g++ is not installed: {str(e)}")
                return {'error': 'g++ compiler is not installed on the server'}

            # Compile the C++ code
            compile_result = subprocess.run(['g++', cpp_file, '-o', os.path.join(temp_dir, 'program')],
                                         capture_output=True,
                                         text=True,
                                         timeout=10)
            
            if compile_result.returncode != 0:
                return {'error': compile_result.stderr.strip()}

            # Run the compiled program
            run_result = subprocess.run([os.path.join(temp_dir, 'program')],
                                      capture_output=True,
                                      text=True,
                                      timeout=10)
            
            if run_result.returncode == 0:
                return {'output': run_result.stdout.strip()}
            else:
                return {'error': run_result.stderr.strip()}
        except subprocess.TimeoutExpired:
            return {'error': 'Code execution timed out after 10 seconds'}
        except Exception as e:
            print(f"Error in execute_cpp: {str(e)}")
            print(traceback.format_exc())
            return {'error': f'C++ execution error: {str(e)}'}

def execute_c(code, filename=None):
    """
    Execute C code and return the output
    """
    print("\n=== C Execution Debug ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Check if gcc is installed
            try:
                gcc_version = subprocess.run(['gcc', '--version'], 
                                          capture_output=True, 
                                          text=True, 
                                          check=True)
                print(f"gcc version: {gcc_version.stdout.split('\n')[0]}")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"Error: gcc is not installed: {str(e)}")
                return {'error': 'gcc compiler is not installed on the server'}

            # Write the C code to a file
            c_file = os.path.join(temp_dir, 'main.c')
            with open(c_file, 'w') as f:
                f.write(code)
            print(f"Created C file: {c_file}")

            # Compile the C code
            compile_result = subprocess.run(['gcc', c_file, '-o', os.path.join(temp_dir, 'program')],
                                         capture_output=True,
                                         text=True,
                                         timeout=10)
            
            if compile_result.returncode != 0:
                return {'error': compile_result.stderr.strip()}

            # Run the compiled program
            run_result = subprocess.run([os.path.join(temp_dir, 'program')],
                                      capture_output=True,
                                      text=True,
                                      timeout=10)
            
            if run_result.returncode == 0:
                return {'output': run_result.stdout.strip()}
            else:
                return {'error': run_result.stderr.strip()}
        except subprocess.TimeoutExpired:
            return {'error': 'Code execution timed out after 10 seconds'}
        except Exception as e:
            print(f"Error in execute_c: {str(e)}")
            print(traceback.format_exc())
            return {'error': f'C execution error: {str(e)}'}

def execute_php(code, filename=None):
    """
    Execute PHP code and return the output
    """
    print("\n=== PHP Execution Debug ===")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
        f.write(code)
        temp_file = f.name
        print(f"Created temporary file: {temp_file}")

    try:
        # Check if PHP is installed
        try:
            php_version = subprocess.run(['php', '-v'], 
                                      capture_output=True, 
                                      text=True, 
                                      check=True)
            print(f"PHP version: {php_version.stdout.split('\n')[0]}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error: PHP is not installed: {str(e)}")
            return {'error': 'PHP is not installed on the server'}

        print(f"Running PHP on file: {temp_file}")
        result = subprocess.run(['php', temp_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        if result.returncode == 0:
            return {'output': result.stdout.strip()}
        else:
            return {'error': result.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {'error': 'Code execution timed out after 10 seconds'}
    except Exception as e:
        print(f"Error in execute_php: {str(e)}")
        print(traceback.format_exc())
        return {'error': f'PHP execution error: {str(e)}'}
    finally:
        try:
            os.unlink(temp_file)
            print(f"Deleted temporary file: {temp_file}")
        except Exception as e:
            print(f"Error deleting temporary file: {str(e)}")

def execute_ruby(code, filename=None):
    """
    Execute Ruby code and return the output
    """
    print("\n=== Ruby Execution Debug ===")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.rb', delete=False) as f:
        f.write(code)
        temp_file = f.name
        print(f"Created temporary file: {temp_file}")

    try:
        # Check if Ruby is installed
        try:
            ruby_version = subprocess.run(['ruby', '-v'], 
                                       capture_output=True, 
                                       text=True, 
                                       check=True)
            print(f"Ruby version: {ruby_version.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error: Ruby is not installed: {str(e)}")
            return {'error': 'Ruby is not installed on the server'}

        print(f"Running Ruby on file: {temp_file}")
        result = subprocess.run(['ruby', temp_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        if result.returncode == 0:
            return {'output': result.stdout.strip()}
        else:
            return {'error': result.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {'error': 'Code execution timed out after 10 seconds'}
    except Exception as e:
        print(f"Error in execute_ruby: {str(e)}")
        print(traceback.format_exc())
        return {'error': f'Ruby execution error: {str(e)}'}
    finally:
        try:
            os.unlink(temp_file)
            print(f"Deleted temporary file: {temp_file}")
        except Exception as e:
            print(f"Error deleting temporary file: {str(e)}")

def execute_go(code, filename=None):
    """
    Execute Go code and return the output
    """
    print("\n=== Go Execution Debug ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Check if Go is installed
            try:
                go_version = subprocess.run(['go', 'version'], 
                                         capture_output=True, 
                                         text=True, 
                                         check=True)
                print(f"Go version: {go_version.stdout.strip()}")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"Error: Go is not installed: {str(e)}")
                return {'error': 'Go is not installed on the server'}

            # Write the Go code to a file
            go_file = os.path.join(temp_dir, 'main.go')
            with open(go_file, 'w') as f:
                f.write(code)
            print(f"Created Go file: {go_file}")

            # Run the Go code
            result = subprocess.run(['go', 'run', go_file], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            if result.returncode == 0:
                return {'output': result.stdout.strip()}
            else:
                return {'error': result.stderr.strip()}
        except subprocess.TimeoutExpired:
            return {'error': 'Code execution timed out after 10 seconds'}
        except Exception as e:
            print(f"Error in execute_go: {str(e)}")
            print(traceback.format_exc())
            return {'error': f'Go execution error: {str(e)}'}

def execute_rust(code, filename=None):
    """
    Execute Rust code and return the output
    """
    print("\n=== Rust Execution Debug ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Check if Rust is installed
            try:
                rust_version = subprocess.run(['rustc', '--version'], 
                                           capture_output=True, 
                                           text=True, 
                                           check=True)
                print(f"Rust version: {rust_version.stdout.strip()}")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"Error: Rust is not installed: {str(e)}")
                return {'error': 'Rust is not installed on the server'}

            # Write the Rust code to a file
            rust_file = os.path.join(temp_dir, 'main.rs')
            with open(rust_file, 'w') as f:
                f.write(code)
            print(f"Created Rust file: {rust_file}")

            # Compile the Rust code
            compile_result = subprocess.run(['rustc', rust_file, '-o', os.path.join(temp_dir, 'program')],
                                         capture_output=True,
                                         text=True,
                                         timeout=10)
            
            if compile_result.returncode != 0:
                return {'error': compile_result.stderr.strip()}

            # Run the compiled program
            run_result = subprocess.run([os.path.join(temp_dir, 'program')],
                                      capture_output=True,
                                      text=True,
                                      timeout=10)
            
            if run_result.returncode == 0:
                return {'output': run_result.stdout.strip()}
            else:
                return {'error': run_result.stderr.strip()}
        except subprocess.TimeoutExpired:
            return {'error': 'Code execution timed out after 10 seconds'}
        except Exception as e:
            print(f"Error in execute_rust: {str(e)}")
            print(traceback.format_exc())
            return {'error': f'Rust execution error: {str(e)}'}

def execute_swift(code, filename=None):
    """
    Execute Swift code and return the output
    """
    print("\n=== Swift Execution Debug ===")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.swift', delete=False) as f:
        f.write(code)
        temp_file = f.name
        print(f"Created temporary file: {temp_file}")

    try:
        # Check if Swift is installed
        try:
            swift_version = subprocess.run(['swift', '--version'], 
                                        capture_output=True, 
                                        text=True, 
                                        check=True)
            print(f"Swift version: {swift_version.stdout.split('\n')[0]}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error: Swift is not installed: {str(e)}")
            return {'error': 'Swift is not installed on the server'}

        print(f"Running Swift on file: {temp_file}")
        result = subprocess.run(['swift', temp_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        if result.returncode == 0:
            return {'output': result.stdout.strip()}
        else:
            return {'error': result.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {'error': 'Code execution timed out after 10 seconds'}
    except Exception as e:
        print(f"Error in execute_swift: {str(e)}")
        print(traceback.format_exc())
        return {'error': f'Swift execution error: {str(e)}'}
    finally:
        try:
            os.unlink(temp_file)
            print(f"Deleted temporary file: {temp_file}")
        except Exception as e:
            print(f"Error deleting temporary file: {str(e)}")

def execute_kotlin(code, filename=None):
    """
    Execute Kotlin code and return the output
    """
    print("\n=== Kotlin Execution Debug ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Check if Kotlin is installed
            try:
                kotlin_version = subprocess.run(['kotlinc', '-version'], 
                                             capture_output=True, 
                                             text=True, 
                                             check=True)
                print(f"Kotlin version: {kotlin_version.stdout.strip()}")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"Error: Kotlin is not installed: {str(e)}")
                return {'error': 'Kotlin is not installed on the server'}

            # Write the Kotlin code to a file
            kotlin_file = os.path.join(temp_dir, 'main.kt')
            with open(kotlin_file, 'w') as f:
                f.write(code)
            print(f"Created Kotlin file: {kotlin_file}")

            # Compile the Kotlin code
            compile_result = subprocess.run(['kotlinc', kotlin_file, '-include-runtime', '-d', os.path.join(temp_dir, 'program.jar')],
                                         capture_output=True,
                                         text=True,
                                         timeout=10)
            
            if compile_result.returncode != 0:
                return {'error': compile_result.stderr.strip()}

            # Run the compiled program
            run_result = subprocess.run(['java', '-jar', os.path.join(temp_dir, 'program.jar')],
                                      capture_output=True,
                                      text=True,
                                      timeout=10)
            
            if run_result.returncode == 0:
                return {'output': run_result.stdout.strip()}
            else:
                return {'error': run_result.stderr.strip()}
        except subprocess.TimeoutExpired:
            return {'error': 'Code execution timed out after 10 seconds'}
        except Exception as e:
            print(f"Error in execute_kotlin: {str(e)}")
            print(traceback.format_exc())
            return {'error': f'Kotlin execution error: {str(e)}'}

def execute_typescript(code, filename=None):
    """
    Execute TypeScript code and return the output
    """
    print("\n=== TypeScript Execution Debug ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Check if TypeScript is installed
            try:
                tsc_version = subprocess.run(['tsc', '--version'], 
                                          capture_output=True, 
                                          text=True, 
                                          check=True)
                print(f"TypeScript version: {tsc_version.stdout.strip()}")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"Error: TypeScript is not installed: {str(e)}")
                return {'error': 'TypeScript is not installed on the server'}

            # Write the TypeScript code to a file
            ts_file = os.path.join(temp_dir, 'main.ts')
            with open(ts_file, 'w') as f:
                f.write(code)
            print(f"Created TypeScript file: {ts_file}")

            # Compile the TypeScript code
            compile_result = subprocess.run(['tsc', ts_file],
                                         capture_output=True,
                                         text=True,
                                         timeout=10)
            
            if compile_result.returncode != 0:
                return {'error': compile_result.stderr.strip()}

            # Run the compiled JavaScript
            js_file = os.path.join(temp_dir, 'main.js')
            run_result = subprocess.run(['node', js_file],
                                      capture_output=True,
                                      text=True,
                                      timeout=10)
            
            if run_result.returncode == 0:
                return {'output': run_result.stdout.strip()}
            else:
                return {'error': run_result.stderr.strip()}
        except subprocess.TimeoutExpired:
            return {'error': 'Code execution timed out after 10 seconds'}
        except Exception as e:
            print(f"Error in execute_typescript: {str(e)}")
            print(traceback.format_exc())
            return {'error': f'TypeScript execution error: {str(e)}'}
