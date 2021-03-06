import subprocess
import json

class Netem(object):

   def __init__(self):
      self.load_config()
      print self.ifaces


   def load_config(self):
      try:
         fname = 'ifaces.conf.json'
         with open(fname) as cf:
             conf = json.load(cf)
         self.ifaces = conf['ifaces']
      except:
         args = ['ls', '/sys/class/net']
         p = subprocess.Popen(args, stdout=subprocess.PIPE)
         self.ifaces = p.communicate()[0].split()
      self.ifaces = filter(self.is_allowed_iface, self.ifaces)
      with open(fname, 'w') as cf:
         json.dump({'ifaces':self.ifaces}, cf)


   def list_ifaces(self):
      return self.ifaces


   def is_allowed_iface(self, dev):
      if 'lo' == dev:
         return False
      return True


   def add_netem(self, dev):
      assert dev
      args = ['tc', 'qdisc', 'add', 'dev', dev, 'root', 'netem', 'delay', '1ms', '0.1ms', 'loss', '0.01%']
      print args
      p = subprocess.Popen(args, stdout=subprocess.PIPE)
      output = p.communicate()[0]


   def get_netem(self, dev):
      assert dev
      print dev
      args = ['tc', 'qdisc', 'show', 'dev', dev]
      print args
      p = subprocess.Popen(args, stdout=subprocess.PIPE)
      output = p.communicate()[0]
            
      return self.parse_tc(output)


   def parse_tc(self, tc_string):
      val = {'conf': tc_string, 'delay':'none', 'd_var':'none', 'loss':'none'};

      parts = tc_string.split()
      print(parts)

      if 'delay' in parts:
         i = parts.index('delay')
         val['delay'] = parts[i+1]
         # is there a word after the delay and does it start with a digit?
         if len(parts) > i+2 and parts[i+2][0].isdigit():
            val['d_var'] = parts[i+2]

      if 'loss' in parts:
         i = parts.index('loss')
         val['loss'] = parts[i+1]

      print(val)
      return val;


   def set_delay(self, dev, d_size, d_variation, loss ):
      assert dev
      curconf = self.get_netem(dev)
      if not curconf['conf'] or 'netem' not in curconf['conf']:
         print "no netem on dev: [%s]. Adding it..." % dev
         self.add_netem(dev)
      args = ['tc', 'qdisc', 'change', 'dev', dev, 'root', 'netem']
      if d_size and d_size[0].isdigit():
         d_size = d_size.replace(" ", "")
         print ("dev: [%s] delay: [%s]" % (dev, d_size))
         args.extend(['delay', d_size]);
      if d_variation and d_variation[0].isdigit():
         d_variation = d_variation.replace(" ", "")
         print ("dev: [%s] jitter: [%s]" % (dev, d_variation))
         args.extend([d_variation]);
      if loss and loss[0].isdigit():
         loss = loss.replace(" ", "")
         print ("dev: [%s] loss: [%s]" % (dev, loss))
         args.extend(['loss', loss])
      print args
      p = subprocess.Popen(args, stdout=subprocess.PIPE)
      return self.get_netem(dev)
      

