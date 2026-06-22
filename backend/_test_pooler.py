import asyncio, sys, os
import psycopg
from dotenv import load_dotenv

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()
url = os.environ["DATABASE_URL"].replace("postgresql+psycopg://", "postgresql://")
netloc = url.split("://", 1)[1].split("@", 1)[0]      # postgres:<encoded_pw>
enc_pw = netloc.split(":", 1)[1]                       # mantém percent-encoding
host_direct = url.split("@", 1)[1].split("/", 1)[0]    # db.<ref>.supabase.co:5432
ref = host_direct.split(".")[1]
user = f"postgres.{ref}"

REGIONS = [
    "us-east-1", "us-east-2", "us-west-1", "us-west-2", "ca-central-1",
    "sa-east-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1",
    "eu-central-2", "eu-north-1", "ap-south-1", "ap-southeast-1",
    "ap-southeast-2", "ap-northeast-1", "ap-northeast-2",
]

async def try_region(region):
    host = f"aws-1-{region}.pooler.supabase.com"
    uri = f"postgresql://{user}:{enc_pw}@{host}:6543/postgres?sslmode=require&connect_timeout=8"
    try:
        conn = await psycopg.AsyncConnection.connect(uri)
        await (await conn.execute("select 1")).fetchone()
        await conn.close()
        print(f"OK   {region}  -> {host}:6543")
        return region
    except Exception as e:
        msg = str(e).splitlines()[0]
        tag = "tenant-not-found" if "not found" in msg.lower() else msg[:60]
        print(f"fail {region:16} {tag}")
        return None

async def main():
    print(f"ref ativo: {ref} | user pooler: {user}")
    found = []
    for r in REGIONS:
        if await try_region(r):
            found.append(r)
    print("\nREGIAO ENCONTRADA:", found or "nenhuma")

asyncio.run(main())
