import glob
import apt_pkg
import os

apt_pkg.init_system()

# Returns the highest version from version array
def highest_version(versions_arr):
  max = versions_arr[0]
  for version in versions_arr:
    if apt_pkg.version_compare(version, max) > 0:
      max = version
  return max

# Return the list of all other versions that are not `highest`
def obsolete_versions(versions_arr, highest):
  return [version for version in versions_arr if version != highest]

# Read .deb files within folder `arch`. `arch` can be i386, amd64, all
def read_files(arch):
  return glob.glob(arch + "/*.deb")

def extract_pkg_info_to_dict(deb_files):
  # dict to store package names and it's info
  pkgs_info = {}

  for file_name in deb_files:
    pkg_name_with_path, version, arch = file_name.split('_')
    package_name = os.path.basename(pkg_name_with_path)

    if package_name in pkgs_info:
      # If there exist already a version array, append this new
      pkgs_info[package_name].append(version)
    else:
      # otherwise create a new array with version being the only element
      pkgs_info[package_name] = [version]

  return pkgs_info

def lower_versioned_files(pkgs_info_dict, arch):
  removable_files  = [] # store file names

  # process the packages
  for package_name in pkgs_info:
    highest = highest_version(pkgs_info[package_name])
    olders = obsolete_versions(pkgs_info[package_name], highest)
    for version in olders:
      removable_files.append(package_name + '_' + version + '_' + arch + '.deb')

  return removable_files

# This function moves files of specific arch.
# arch can be 'amd64', 'i386', 'all'
def move_files(file_list, arch):
  #Create destination folder
  target_dir = "removables/" + arch + "/"
  if (not os.path.exists(target_dir)):
    os.makedirs(target_dir)

  for file in file_list:
    print(file + "  -->  " + target_dir + file )
    os.rename(arch + "/" + file, target_dir + file)

archs = ['amd64', 'i386', 'all']

for arch in archs:
  deb_files = read_files(arch)
  pkgs_info = extract_pkg_info_to_dict(deb_files)
  lower_versioned = lower_versioned_files(pkgs_info, arch)
  move_files(lower_versioned, arch)