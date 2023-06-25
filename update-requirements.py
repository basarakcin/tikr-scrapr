import os
import subprocess

# Check if the virtual environment is already activated
if not os.environ.get('VIRTUAL_ENV'):
    # Path to the activate script within the virtual environment
    activate_script = 'env-tikr/bin/activate'
    
    # Execute the activate script using the bash shell
    print("Activating virtual environment...")
    subprocess.run(f'bash -c "source {activate_script}"', shell=True)
else:
    print("Virtual environment is already activated.")

# Update the requirements.txt file
print("Updating requirements...")
result = subprocess.run(['pip', 'freeze', '--local'], capture_output=True, text=True)
requirements = result.stdout.strip().split('\n')
filtered_requirements = [r for r in requirements if not r.startswith('-e')]
requirements_text = '\n'.join(filtered_requirements)
print(requirements_text) # DEBUG HELPER

with open('requirements.txt', 'w') as file:
    file.write(requirements_text)
    
print("Requirements updated successfully!")