#!/usr/bin/python


import sys
import os
import optparse
import subprocess
import tempfile
import shutil
from xml.etree import ElementTree
import plistlib
from Foundation import NSData, \
                       NSPropertyListSerialization, \
                       NSPropertyListMutableContainers, \
                       NSPropertyListXMLFormat_v1_0

                       
class FoundationPlistException(Exception):
    pass

class NSPropertyListSerializationException(FoundationPlistException):
    pass

def readPlist(path):
    plistData = NSData.dataWithContentsOfFile_(path)
    dataObject, plistFormat, error = \
        NSPropertyListSerialization.propertyListFromData_mutabilityOption_format_errorDescription_(
        plistData, NSPropertyListMutableContainers, None, None)
    if error:
        errmsg = "%s in file %s" % (repr(error), repr(path))
        raise NSPropertyListSerializationException(errmsg)
    else:
        return dataObject
    

def parse_info_plist(plist_path):
    ##print plist_path
    return readPlist(plist_path)
    

ID_KEYS = set(("CFBundleIdentifier", "CFBundleName"))
VERSION_KEYS = set(("CFBundleShortVersionString", "CFBundleVersion"))

def bundle_dict(abs_path, target_path):
    bundle = dict()
    try:
        info = parse_info_plist(abs_path)
    except:
        return None
    bundle["path"] = target_path.rsplit("/Contents/Info.plist", 1)[0]
    if bundle["path"].lower().endswith(".app"):
        bundle["type"] = "application"
    else:
        bundle["type"] = "bundle"
    for key in ("CFBundleIdentifier",
                "CFBundleName",
                "CFBundleShortVersionString",
                "CFBundleVersion"):
        try:
            bundle[key] = info[key]
        except KeyError:
            pass
    # Require a name or bundle ID.
    if not ID_KEYS.intersection(set(bundle.keys())):
        return None
    # Require at least one of the version keys.
    if not VERSION_KEYS.intersection(set(bundle.keys())):
        return None
    return bundle
    

def generate_info_plists(path):
    ##print "generate_info_plists(%s)" % repr(path)
    if not path.endswith("/"):
        path = path + "/"
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.lower() == "info.plist":
                yield (os.path.join(dirpath, filename),
                       os.path.join(dirpath.replace(path, "", 1), filename))
    

def expand_flat_pkg(flat_pkg_path):
    ##print "expand_flat_pkg(%s)" % repr(flat_pkg_path)
    tmp_path = tempfile.mkdtemp()
    expanded_pkg_path = os.path.join(tmp_path, "pkg")
    try:
        subprocess.check_call(("/usr/sbin/pkgutil",
                               "--expand",
                               flat_pkg_path,
                               expanded_pkg_path))
        return expanded_pkg_path
    except:
        shutil.rmtree(expanded_pkg_path, ignore_errors=True)
        raise
    

def parse_packageinfo(packageinfo_path):
    info = dict()
    pi = ElementTree.parse(packageinfo_path)
    ##print pi.getroot().items()
    target = pi.getroot().get("install-location")
    if target:
        info["target"] = target
    else:
        info["target"] = "/"
    ##print info
    return info
    

def generate_items_from_flat_payload(flat_payload_path):
    ##print "generate_items_from_flat_payload(%s)" % repr(flat_payload_path)
    packageinfo_path = os.path.join(flat_payload_path, "PackageInfo")
    pkg_info = parse_packageinfo(packageinfo_path)
    payload_path = os.path.join(flat_payload_path, "Payload")
    expanded_payload_path = tempfile.mkdtemp()
    try:
        subprocess.check_call(("/usr/bin/ditto",
                               "-x",
                               payload_path,
                               expanded_payload_path))
        for abspath, relpath in generate_info_plists(expanded_payload_path):
            bd = bundle_dict(abspath, os.path.join(pkg_info["target"], relpath))
            if bd:
                yield bd
    finally:
        shutil.rmtree(expanded_payload_path, ignore_errors=True)
    

def generate_items_from_flat_pkg(flat_pkg_path):
    ##print "generate_items_from_flat_pkg(%s)" % repr(flat_pkg_path)
    expanded_pkg_path = expand_flat_pkg(flat_pkg_path)
    try:
        # If this is a distribution package, recursively call generate on the
        # sub-packages.
        dist_path = os.path.join(expanded_pkg_path, "Distribution")
        if os.path.exists(dist_path):
            dist = ElementTree.parse(dist_path)
            for pkgref in dist.iter("pkg-ref"):
                ##print pkgref.items()
                if pkgref.text:
                    ##print pkgref.text
                    pkg_path = pkgref.text
                    # Payload packages inside the flat archive are prefixed with #.
                    if pkg_path.startswith("#"):
                        payload_path = os.path.join(expanded_pkg_path,
                                                    pkg_path[1:])
                        for item in generate_items_from_flat_payload(payload_path):
                            yield item
                    else:
                        # Otherwise we have a URL.
                        if pkg_path.startswith("file:"):
                            payload_pkg_path = os.path.join(os.path.dirname(flat_pkg_path),
                                                            pkg_path[5:])
                            for item in generate_items_from_pkg(payload_pkg_path):
                                yield item
                        else:
                            pass
                            #sys.exit("Unsupported package path: %s" % pkg_path)
        else:
            # Otherwise we unpack the payload.
            for item in generate_items_from_flat_payload(expanded_pkg_path):
                yield item
    finally:
        shutil.rmtree(expanded_pkg_path, ignore_errors=True)
    

def generate_items_from_pkg(pkg_path):
    ##print "generate_from_pkg(%s)" % repr(pkg_path)
    try:
        if os.path.isdir(pkg_path):
            for item in generate_items_from_bundle_pkg(pkg_path):
                yield item
        else:
            for item in generate_items_from_flat_pkg(pkg_path):
                yield item
    except subprocess.CalledProcessError, e:
        sys.exit("Extraction of %s failed: %s" % (pkg_path, e))
    

def main(argv):
    p = optparse.OptionParser()
    p.set_usage("""Usage: %prog [options] package.(m)pkg""")
    p.add_option("-v", "--verbose", action="store_true",
                 help="Verbose output.")
    options, argv = p.parse_args(argv)
    if len(argv) != 2:
        print >>sys.stderr, p.get_usage()
        return 1
    
    root_pkg_path = argv[1]
    pkginfo = {
        "installs": list(),
    }
    for item in generate_items_from_pkg(root_pkg_path):
        pkginfo["installs"].append(item)
    
    print plistlib.writePlistToString(pkginfo)
    
    return 0
    

if __name__ == '__main__':
    sys.exit(main(sys.argv))
    
