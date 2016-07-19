// Fill out your copyright notice in the Description page of Project Settings.
//Based on a tutorial from here: https://wiki.unrealengine.com/Custom_input_device_plugin_guide


//The goal of this plugin is to Fire up a SOCKET, and then to read from a feaux controller, the current position of the actor, exactly.
//Then, to send it off to an actor to reposition themselves.
using UnrealBuildTool;

public class QuickStart : ModuleRules
{
	public QuickStart(TargetInfo Target)
	{
        PublicIncludePaths.AddRange(
        new string[] {
                "Developer/AssetTools/Public",
                    "Editor/UnrealEd/Public",
                    "Editor/UnrealEd/Classes",
            // ... add public include paths required here ...
        });

        PrivateIncludePaths.AddRange(
            new string[] {
                            "Developer/m2uPlugin/Private",
                            "Editor/UnrealEd/Public",
                            "Editor/UnrealEd/Classes",
                            "Editor/UnrealEd/Private",
                            "Editor/UnrealEd/Private/Fbx",
					        // ... add other private include paths required here ...
					});

        PublicDependencyModuleNames.AddRange(new string[] { "Core",
            "CoreUObject",
            "Engine",
            "HeadMountedDisplay",
            "InputCore",
            "Sockets",
            "Networking" });

		PrivateDependencyModuleNames.AddRange(new string[] {  });

	}
}
