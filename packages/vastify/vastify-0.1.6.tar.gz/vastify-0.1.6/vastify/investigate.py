from .instance import Instance
import asyncio

async def main():
    requirements = dict(gpu_name="RTX_2080_Ti",
                price=0.25,
                disk=100.0,
                image='python:3.10-slim',
                num_gpus='1',
                regions=['North_America','Europe', 'World'],
                env='-p 70000:8000')

    instance = await Instance.from_requirements(requirements)

    instance.run_command("ls -la")

    print(instance)


if __name__ == "__main__":
    asyncio.run(main())