import os

from track_service import read_gps_file
from track_service import visualize
from track_service import preview_frame
from track_service import animated
from track_service import Crate_map_video
from track_service import tcx_to_json
from mail_service import get_new_mails
from mail_service import send_mail
from mail_service import move_mail
from pathlib import Path
import shutil


def main():
    mails = get_new_mails()
    for mailData in mails:
        jsonFile = tcx_to_json(mailData['filepath'])
        df = read_gps_file(jsonFile)
        #visualize(df)
        #preview_frame(df)
        #animated(df)
        data = Crate_map_video(df, mailData)
        send_mail(data.outputnames)
        remove_files()
        move_mail('TrackToMp4')


def remove_files():
    exportPath = Path(__file__).parent.parent / 'export'
    print(exportPath)
    for file in os.listdir(exportPath):
        print(file)
        if os.path.isfile(os.path.join(exportPath, file)):
            os.remove(os.path.join(exportPath, file))
        else:
            shutil.rmtree(os.path.join(exportPath, file))

if __name__ == '__main__':
    main()

