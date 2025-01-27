import os
from typing import List
from dv_flow.mgr import Task, TaskData
from dv_flow.libhdlsim.vl_sim_image import VlSimImage

class SimImage(VlSimImage):

    def getRefTime(self):
        if os.path.isfile(os.path.join(self.rundir, 'simv_opt.d')):
            print("Returning timestamp")
            return os.path.getmtime(os.path.join(self.rundir, 'simv_opt.d'))
        else:
            raise Exception("simv_opt.d file (%s) does not exist" % os.path.join(self.rundir, 'simv_opt.d'))
    
    async def build(self, files : List[str], incdirs : List[str]):
        cmd = []

        cmd = ['xvlog', '--sv']

        for incdir in incdirs:
            cmd.extend(['-i', incdir])

        cmd.extend(files)

        print("self.basedir=%s" % self.rundir)
        proc = await self.session.create_subprocess(*cmd,
                                                        cwd=self.rundir)
        await proc.wait()

        if proc.returncode != 0:
            raise Exception("xvlog failed (%d)" % proc.returncode)

        # Now, run vopt
        cmd = ['xelab', '--snapshot', 'simv.snap']
        for top in self.params.top:
            cmd.append(top)

        proc = await self.session.create_subprocess(*cmd,
                                                        cwd=self.rundir)
        await proc.wait()

        if proc.returncode != 0:
            raise Exception("xelab failed (%d)" % proc.returncode)

