import os
import shutil

def create_html_from_template():
    while True:
        try:
            print("\n" + "="*40)
            print("HTML File Creator (Ctrl+C to exit)")
            print("="*40)
            
            # Get user input
            filename = input("\nEnter the filename (with or without .html extension): ").strip()
            if not filename:
                print("Error: Filename cannot be empty. Please try again.")
                continue
                
            description = input("Enter the description to replace 'Index': ").strip()
            if not description:
                print("Error: Description cannot be empty. Please try again.")
                continue

            # Ensure filename ends with .html
            if not filename.lower().endswith('.html'):
                filename += '.html'

            # Check if template exists
            template_path = 'template_page.html'
            if not os.path.exists(template_path):
                print(f"Error: Template file '{template_path}' not found in the current directory.")
                print("Please make sure template_page.html exists in the same folder.")
                continue

            # Check if target file already exists
            if os.path.exists(filename):
                overwrite = input(f"Warning: '{filename}' already exists. Overwrite? (y/n): ").lower()
                if overwrite != 'y':
                    print("Operation cancelled.")
                    continue

            # Copy and modify the file
            shutil.copyfile(template_path, filename)
            
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
            
            modified_content = content.replace('Index', description)
            
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(modified_content)
                
            print(f"\nSuccess! File '{filename}' has been created with your description.")
            print("You may now exit the program (Ctrl+C) or create another file.")
            
        except KeyboardInterrupt:
            print("\nExiting program. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    create_html_from_template()
