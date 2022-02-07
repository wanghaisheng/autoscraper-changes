#! /bin/bash
cd data
clear
echo "https://github.com/clientcrash/Tikgen"
echo Generating TikTok Compilation...
echo "Downloading $1 top videos from /r/TikTokCringe/top.json"
youtube-dl $(curl -s -H "User-agent: 'TCompV1: v1.0'" https://www.reddit.com/r/TikTokCringe/top.json\?limit=$1 | jq '.' | grep url_overridden_by_dest | grep -Eoh "https:\/\/v\.redd\.it\/\w{13}")

for f in *.mp4; do clear ; echo "generating blur version for $f" ; ffmpeg -i $f -lavfi '[0:v]scale=ih*16/9:-1,boxblur=luma_radius=min(h\,w)/20:luma_power=1:chroma_radius=min(cw\,ch)/20:chroma_power=1[bg];[bg][0:v]overlay=(W-w)/2:(H-h)/2,crop=h=iw*9/16' -vb 800K ./blur/$f -hide_banner -loglevel warning; done
echo "Deleting normal versions..."
rm *.mp4
echo "Writing blur video file names to files.txt"
for f in data/*.mp4; do echo "file $f" >> files.txt ; done
echo merging files...
ffmpeg -f concat -i files.txt ./data/result.mp4 -hide_banner -loglevel warning
cp ./data/result.mp4 ./result.mp4
rm ./data/*.mp4
rm files.txt
echo DONE
echo "I only created this script to practice my bash coding..."
