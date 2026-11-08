# SpaceUnpack

SpaceUnpack extracts archives without needing double the disk space.

A normal extractor writes the full contents next to the archive, so a 50 GB archive needs roughly 100 GB free. SpaceUnpack gives the archive's space back while it extracts, so you only need room for the extracted files. It installs like a normal Windows program and adds a right-click menu to your archives.

What it can do

Choose what to extract. Open a ZIP and tick the files and folders you want. Select all and Select none help with long lists.

Right-click menu. Right-click any archive and choose SpaceUnpack to extract to a folder, extract here, or shrink the zip as it goes.

Modern look. The window follows your Windows light or dark setting.

Passwords. Password-protected ZIP files are supported.

Safe by design. Archives that try to write outside the folder you chose are refused.

The three modes

Safe is the default. It extracts everything, then deletes the archive. You need room for the archive and the extracted files at the same time. If anything goes wrong, the archive is kept untouched.

Shrink works on ZIP files only. It removes each file from the zip as soon as that file is extracted, so the zip gets smaller while the folder grows. You only need room for the extracted files plus a little extra. If it stops, the zip stays valid and still holds the files that were not extracted yet, so you can run it again to continue. It works on any drive.

Low-space gives the most saving, even inside one huge file. It frees the archive's disk space while reading it, but the archive is destroyed in the process. If extraction fails or is cancelled, the archive cannot be recovered. It needs an NTFS drive on Windows.

Supported formats

ZIP, TAR, TAR.GZ, TAR.BZ2, TAR.XZ, and single .gz, .bz2 and .xz files. 7Z and RAR files work in Safe mode if 7-Zip or unrar is installed.

How to install

Download and run SpaceUnpack-Setup.exe. You do not need administrator rights or Python. Keep the option "Add SpaceUnpack to the right-click menu" ticked. Then right-click an archive and choose SpaceUnpack. On Windows 11, click "Show more options" first. To remove it, open Windows Settings, then Apps, then SpaceUnpack, and choose Uninstall.

Good to know

If you choose only some files, the archive is always kept, because the files you did not choose are still inside it.

A zip that is one single huge file saves nothing in Shrink mode until that file is finished.

Multi-part archives such as .part1.rar and .z01 are not supported, and SpaceUnpack cannot create archives.

The installer is not code-signed, so Windows may show a "protected your PC" notice. Click More info, then Run anyway.

The source code is available, and the tool also runs from source on Linux.
