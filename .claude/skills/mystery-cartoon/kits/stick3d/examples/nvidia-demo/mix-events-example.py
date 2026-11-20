import subprocess
ev=[(1.16,'impact',-8),(1.16,'roll',-17),(4.69,'whoosh',-13),(6.77,'pop',-12),(7.9,'swing',-15),(8.31,'stamp',-12),(8.93,'whoosh',-13),
(9.2,'stamp',-17),(9.62,'stamp',-17),(10.02,'stamp',-17),(10.42,'stamp',-17),(10.8,'stamp',-17),(10.98,'slash',-13),(11.5,'impact',-11),(12.36,'stamp',-8),
(13.29,'whoosh',-13),(15.77,'lock',-12),(15.8,'swing',-16),(16.97,'pop',-9),(17.45,'riser',-18),(17.69,'impact',-10),(18.7,'riser',-15),(19.07,'heart',-11),(21.2,'impact',-11)]
ev+=[(3.43+i*0.13,'tick',-14) for i in range(6)]
ins=['-i','vo/out/voiceover-trimmed.wav']; fl=[]; lab=['[0:a]']
for i,(t,n,db) in enumerate(ev,1):
    ins+=['-i',f'sfx/{n}.wav']; fl.append(f'[{i}:a]volume={db}dB,adelay={int(t*1000)}|{int(t*1000)}[s{i}]'); lab.append(f'[s{i}]')
fl.append(''.join(lab)+f'amix=inputs={len(lab)}:normalize=0,alimiter=limit=0.95,apad=whole_dur=22[a]')
subprocess.run(['ffmpeg','-y','-v','error',*ins,'-filter_complex',';'.join(fl),'-map','[a]','-t','22','-ar','48000','mix.wav'],check=True)
