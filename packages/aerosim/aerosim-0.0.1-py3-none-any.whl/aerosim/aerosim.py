import json
import os

# AeroSim packages
import aerosim_world
import aerosim_renderer_adapter_ue5
import aerosim_renderer_adapter_rtx


class AeroSim:
    def __init__(self) -> None:
        self.sim_config_json = None
        self.aerosim_orchestrator = None
        self.aerosim_renderer_adapter = None
        self.aerosim_fmudrivers = []

    def run(self, sim_config_file: str, sim_config_dir: str = os.getcwd()):
        # ----------------------------------------------
        # Load the sim configuration
        sim_config_path = os.path.abspath(os.path.join(sim_config_dir, sim_config_file))
        print(f"Loading simulation configuration from {sim_config_path}...")
        with open(sim_config_path, "r") as file:
            self.sim_config_json = json.load(file)

        # print("Simulation configuration loaded:")
        # print(json.dumps(self.sim_config_json, indent=4))

        # ----------------------------------------------
        # Initialize AeroSim components

        print("Initializing AeroSim Orchestrator...")
        self.aerosim_orchestrator = aerosim_world.Orchestrator()

        print("Choosing Renderer Adapter...")
        inifile_path = "../renderer_config.ini"
        if os.path.exists(inifile_path):
            with open(inifile_path, "r") as file:
                file_content = file.read()

            if "UE5" in file_content:
                # TODO Switch loading adapter based on the renderer chosen in the sim config
                print("Initializing UE5 AeroSim Renderer Adapter...")
                self.aerosim_renderer_adapter = (
                    aerosim_renderer_adapter_ue5.RendererAdapterUE5(
                        json.dumps(self.sim_config_json)
                    )
                )

            if "Omniverse" in file_content:
                # TODO Switch loading adapter based on the renderer chosen in the sim config
                print("Initializing RTX AeroSim Renderer Adapter...")
                self.aerosim_renderer_adapter = (
                    aerosim_renderer_adapter_rtx.RendererAdapterRTX()
                )
        else:
            print(
                "WARNING: No renderer_config.ini file found. If rendering is needed, please run launch_aerosim.bat/sh script to select one."
            )
            input("Press any key to continuing without rendering.")

        for fmu_config in self.sim_config_json["fmu_models"]:
            print(f"Initializing AeroSim FMU Driver '{fmu_config["id"]}'...")
            self.aerosim_fmudrivers.append(
                aerosim_world.FmuDriver(fmu_config["id"], sim_config_dir)
            )

        # ----------------------------------------------
        # Load AeroSim components

        # Load orchestrator first because it creates the topics
        print("Loading AeroSim Orchestrator...")
        self.aerosim_orchestrator.load(json.dumps(self.sim_config_json))

        if self.aerosim_renderer_adapter is not None:
            print("Loading AeroSim Renderer Adapter...")
            self.aerosim_renderer_adapter.load()

        # ----------------------------------------------
        # Start AeroSim components

        for fmu_driver in self.aerosim_fmudrivers:
            print(f"Starting AeroSim FMU Driver '{fmu_driver.fmu_id}'...")
            fmu_driver.start()

        if self.aerosim_renderer_adapter is not None:
            print("Starting AeroSim Renderer Adapter...")
            self.aerosim_renderer_adapter.start()

        print("Starting AeroSim Orchestrator...")
        self.aerosim_orchestrator.start()

    def stop(self):
        self.aerosim_orchestrator.stop()
        if self.aerosim_renderer_adapter is not None:
            self.aerosim_renderer_adapter.stop()
        for fmu_driver in self.aerosim_fmudrivers:
            fmu_driver.stop()
        print("Finished.")
