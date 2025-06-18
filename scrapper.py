import aiohttp,asyncio,datetime,time,socket,os
from colorama import Fore,init
init()
pc_name=socket.gethostname()
st=datetime.datetime.utcnow().strftime("%Y-%m-%D %H:%M:%S")
l=asyncio.Lock()
rl={}

banner=f"""{Fore.RED}

              ██████  ██▀███   ██▒   █▓  ██████  ▄████▄   ██▀███   ▄▄▄       ██▓███  
            ▒██    ▒ ▓██ ▒ ██▒▓██░   █▒▒██    ▒ ▒██▀ ▀█  ▓██ ▒ ██▒▒████▄    ▓██░  ██▒
            ░ ▓██▄   ▓██ ░▄█ ▒ ▓██  █▒░░ ▓██▄   ▒▓█    ▄ ▓██ ░▄█ ▒▒██  ▀█▄  ▓██░ ██▓▒
              ▒   ██▒▒██▀▀█▄    ▒██ █░░  ▒   ██▒▒▓▓▄ ▄██▒▒██▀▀█▄  ░██▄▄▄▄██ ▒██▄█▓▒ ▒
            ▒██████▒▒░██▓ ▒██▒   ▒▀█░  ▒██████▒▒▒ ▓███▀ ░░██▓ ▒██▒ ▓█   ▓██▒▒██▒ ░  ░
            ▒ ▒▓▒ ▒ ░░ ▒▓ ░▒▓░   ░ ▐░  ▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░░ ▒▓ ░▒▓░ ▒▒   ▓▒█░▒▓▒░ ░  ░
            ░ ░▒  ░ ░  ░▒ ░ ▒░   ░ ░░  ░ ░▒  ░ ░  ░  ▒     ░▒ ░ ▒░  ▒   ▒▒ ░░▒ ░     
            ░  ░  ░    ░░   ░      ░░  ░  ░  ░  ░          ░░   ░   ░   ▒   ░░       
                  ░     ░           ░        ░  ░ ░         ░           ░  ░         
                                   ░            ░                                    
                                                                       
                                {Fore.WHITE}Started: {st}
                                {Fore.WHITE}Author: NightKikko
                                {Fore.WHITE}Your Device: {pc_name}{Fore.RESET}\n"""

def fm(p,m):return f"  {Fore.RED}[{Fore.WHITE}!{Fore.RED}]{Fore.RESET} {m}"

async def w(u,p,gid,gname,cid,cname,ts,c,a,em):
 async with l:
  if c.strip()or a or em:
   with open(f"users/{u}.txt","a",encoding="utf-8")as f:
    f.write(f"[{ts}] ({gid}/{gname} | {cid}/{cname}) [{p}]: {c}\n")
    if a:f.write(''.join(f"   • Pièce jointe: {x['url']} [{x['filename']}]\n"for x in a))
    if em:f.write(''.join(f"   • {'Embed: '+e.get('title','')+chr(10) if'title'in e else''}{'Description: '+e.get('description','')+chr(10) if'description'in e else''}{'Image: '+e['image']['url']+chr(10) if'image'in e and'url'in e['image']else''}"for e in em))

async def gj(s,u,p=None):
 global rl;r=0
 while r<5:
  bucket=u.split('/')[4]if'channels'in u else'global'
  if bucket in rl and rl[bucket]>time.time():await asyncio.sleep(rl[bucket]-time.time())
  try:
   async with s.get(u,params=p)as x:
    if'X-RateLimit-Remaining'in x.headers and x.headers['X-RateLimit-Remaining']=='0':rl[bucket]=float(x.headers['X-RateLimit-Reset'])
    if x.status==200:return await x.json()
    if x.status==429:await asyncio.sleep(float(x.headers.get('retry-after',1.0)));r+=1;continue
    return None
  except:return None

async def main():
 os.system('cls')
 print(banner)
 print(f"   {Fore.RED}┌───({Fore.RESET}{pc_name}{Fore.RED})")
 token=input(f"{Fore.RED}   └──$ {Fore.RESET}Token Discord: ").strip()
 show_no_perm=input(f"{Fore.RED}   └──$ {Fore.RESET}Afficher les salons sans permission ? (o/n): ").lower()=='o'
 print(fm("Info","Démarrage du scraping..."))
 h={"Authorization":token}
 async with aiohttp.ClientSession(headers=h)as s:
  gs=await gj(s,"https://discord.com/api/v9/users/@me/guilds")
  if not gs:print(fm("Erreur","Token invalide ou aucun serveur"));return
  print(fm("Info",f"Serveurs trouvés: {len(gs)}"))
  for g in gs:
   gid=g['id'];gname=g.get('name','?')
   print(fm("Info",f"Scan serveur: {gname} ({gid})"))
   cs=await gj(s,f"https://discord.com/api/v9/guilds/{gid}/channels")
   if not cs:continue
   for c in cs:
    if type(c)!=dict or c.get('type',0)not in[0,5]:continue
    cid=c['id'];cname=c.get('name','?')
    ms=await gj(s,f"https://discord.com/api/v9/channels/{cid}/messages",{"limit":1})
    if not ms:
     if show_no_perm:print(fm("Erreur",f"Pas de permission pour: {cname} ({cid})"))
     continue
    print(fm("Info",f"Scan salon: {cname} ({cid})"))
    m_id,n=None,0
    while 1:
     msgs=await gj(s,f"https://discord.com/api/v9/channels/{cid}/messages",{"limit":100,"before":m_id}if m_id else{"limit":100})
     if not msgs:break
     for m in msgs:
      if m.get('type',0)!=0 or m.get('webhook_id')or m.get('author',{}).get('bot',False):continue
      a=m['author']['id'];p=m['author'].get('global_name')or m['author']['username']
      ts=datetime.datetime.fromisoformat(m['timestamp'].replace('Z','+00:00')if'Z'in m['timestamp']else m['timestamp']).strftime('%d/%m/%Y %H:%M')
      contenu=m.get('content','');att=m.get('attachments',[]);embeds=m.get('embeds',[])
      if contenu.strip()or att or(embeds and any('title'in e or'description'in e or('image'in e and'url'in e['image'])for e in embeds)):
       await w(a,p,gid,gname,cid,cname,ts,contenu,att,embeds)
       n+=1
       if n%10==0:print(fm("Debug",f"Messages: {n} | Dernier: {p} dans {cname}"),end="\r")
     m_id=msgs[-1]['id']
    print(fm("Succès",f"Messages indexés: {n}"))
 print(fm("Info","Terminé!"))

if __name__=="__main__":
 try:import os;os.makedirs("users",exist_ok=True)
 except:pass
 asyncio.run(main())