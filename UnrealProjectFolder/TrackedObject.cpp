//UE4 Networking thanks to StackOverflow and Rama from UE4 Forums.

#include "QuickStart.h"
#include "TrackedObject.h"

//#include "SocketsPrivatePCH.h"
//#include "SocketSubsystem.h"

// Sets default values
ATrackedObject::ATrackedObject()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;
	Connected = false;
	left = true;
	currentLocation = FVector::FVector(0, 0, 80);
}

// Called when the game starts or when spawned
void ATrackedObject::BeginPlay()
{
	Super::BeginPlay();
	// Initiate your device here
	//IP = 127.0.0.1, Port = 8890 for test case

	//FString IP = TEXT("127.0.0.1"); //LOCAL TESTING
	FString IP = TEXT("169.254.185.157");

	if (!StartTCPReceiver("RamaSocketListener", IP, 8890))
	{
		//Starting the receiver failed, don't bother listening
		UE_LOG(LogTemp, Warning, TEXT("Unable to start the listener!"));
		return;
	}

	UE_LOG(LogTemp, Warning, TEXT("Started the listener!."));
	}

// Called every frame
void ATrackedObject::Tick( float DeltaTime )
{
	Super::Tick( DeltaTime );
	
	if (!Connected)
	{
		FVector NewLocation = this->GetActorLocation();
		if (left)
			NewLocation.Y += .5;
		else
			NewLocation.Y -= .5;

		if (NewLocation.Y > 360.0)
			left = false;
		else if (NewLocation.Y < 0.0)
			left = true;

		SetActorLocation(NewLocation);
	}
	//else
		//TCPSocketListener();
	
}

bool ATrackedObject::StartTCPReceiver(const FString& YourChosenSocketName, const FString& TheIP, const int32 ThePort)
{
	ListenerSocket = CreateTCPConnectionListener(YourChosenSocketName, TheIP, ThePort);

	//Not created?
	if (!ListenerSocket)
	{
		GEngine->AddOnScreenDebugMessage(-1, 5.f, FColor::Red, FString::Printf(TEXT("StartTCPReceiver>> Listen socket could not be created! ~> %s %d"), *TheIP, ThePort));
		return false;
	}

	//TODO: Find better way of doing this!
	GetWorldTimerManager().SetTimer(TimerHandle_Connection, this, &ATrackedObject::TCPConnectionListener, 0.01, true);

	return true;
}
//Format IP String as Number Parts
bool ATrackedObject::FormatIP4ToNumber(const FString& TheIP, uint8(&Out)[4])
{
	//IP Formatting
	TheIP.Replace(TEXT(" "), TEXT(""));

	//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	//						   IP 4 Parts
	const TCHAR *delim;
	delim = TEXT(".");
	//String Parts
	//
	TArray<FString> Parts;
	TheIP.ParseIntoArray(Parts, delim);

	if (Parts.Num() != 4)
		return false;

	//String to Number Parts
	for (int32 i = 0; i < 4; ++i)
	{
		Out[i] = FCString::Atoi(*Parts[i]);
	}

	return true;
}

bool ATrackedObject::SplitByteArrayToCharNumber(const FString& toSplit, float(&Out)[2])
{
	const TCHAR * delim = TEXT(",");
	TArray<FString> Parts;
	toSplit.ParseIntoArray(Parts, delim);

	if (Parts.Num() != 2)
		return false;

	for (int32 i = 0; i < 2; ++i)
	{
		Out[i] = FCString::Atoi(*Parts[i]);
	}
	return true;
}

//Create Listener
FSocket* ATrackedObject::CreateTCPConnectionListener(const FString& YourChosenSocketName, const FString& TheIP, const int32 ThePort, const int32 ReceiveBufferSize)
{
	uint8 IP4Nums[4];
	if (!FormatIP4ToNumber(TheIP, IP4Nums))
	{
		UE_LOG(LogTemp, Log, TEXT("Invalid IP! Expecting 4 parts separated by ."));
		return false;
	}

	//Create Socket
	FIPv4Endpoint Endpoint(FIPv4Address(IP4Nums[0], IP4Nums[1], IP4Nums[2], IP4Nums[3]), ThePort);
	FSocket* ListenSocket = FTcpSocketBuilder(*YourChosenSocketName)
		.AsReusable()
		.BoundToEndpoint(Endpoint)
		.Listening(7);
		

	//Set Buffer Size
	int32 NewSize = 0;
	ListenSocket->SetReceiveBufferSize(ReceiveBufferSize, NewSize);

	//Done!
	return ListenSocket;
}

void ATrackedObject::TCPConnectionListener()
{
	//~~~~~~~~~~~~~
	if (!ListenerSocket) return;
	//~~~~~~~~~~~~~
	UE_LOG(LogTemp, Verbose, TEXT("Listening for connections still!"));

	//Remote address
	TSharedRef<FInternetAddr> RemoteAddress = ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->CreateInternetAddr();
	bool Pending;

	// handle incoming connections
	if (ListenerSocket->HasPendingConnection(Pending) && Pending)
	{
		UE_LOG(LogTemp, Warning, TEXT("Handle Incoming!"));
		//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		//Already have a Connection? destroy last one
		if (ConnectionSocket)
		{
			ConnectionSocket->Close();
			ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(ConnectionSocket);
		}
		//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		//New Connection receive!
		ConnectionSocket = ListenerSocket->Accept(*RemoteAddress, TEXT("RamaTCP Received Socket Connection"));

		if (ConnectionSocket != NULL)
		{
			//Global cache of current Remote Address
			RemoteAddressForConnection = FIPv4Endpoint(RemoteAddress);

			//UE_LOG "Accepted Connection! WOOOHOOOO!!!";
			GetWorldTimerManager().SetTimer(TimerHandle_Socket, this, &ATrackedObject::TCPSocketListener, 0.005, true);
			Connected = true;
			//can thread this too
		}
	}
}

//Get a string From Binary Array
//requires #include <string>
FString ATrackedObject::StringFromBinaryArray(const TArray<uint8>& BinaryArray)
{
	//Create a string from a byte array!
	std::string cstr(reinterpret_cast<const char*>(BinaryArray.GetData()), BinaryArray.Num());
	return FString(cstr.c_str());
}

//TCP Socket Listener
void ATrackedObject::TCPSocketListener()
{
	//~~~~~~~~~~~~~
	if (!ConnectionSocket)
	return;
	//~~~~~~~~~~~~~

	//Binary Array!
	TArray<uint8> ReceivedData;

	uint32 Size;
	while (ConnectionSocket->HasPendingData(Size))
	{
		ReceivedData.Init(0, FMath::Min(Size, 65507u));

		int32 Read = 0;
		ConnectionSocket->Recv(ReceivedData.GetData(), ReceivedData.Num(), Read);
	}

	//No data or too much received.
	if (ReceivedData.Num() <= 0 || ReceivedData.Num() > 10)
		return;

	UE_LOG(LogTemp, Log, TEXT("Total Data read : %d"), ReceivedData.Num());
	

	//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	//	Rama's String From Binary Array
	const FString ReceivedUE4String = StringFromBinaryArray(ReceivedData);
	//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	//GEngine->AddOnScreenDebugMessage(-1, 5.f, FColor::Black, FString::Printf(TEXT("As String Data ~> %s"), *ReceivedUE4String));
	
	float newLocation[2];
	if (this->SplitByteArrayToCharNumber(ReceivedUE4String, newLocation))
	{
		FVector NewLocation = GetActorLocation();
		NewLocation.Y = newLocation[0];       //Range of 0 - 360 
		NewLocation.Z = (300.0 - newLocation[1]); //(240.0 - newLoc[1]) + 60 For a range of 0-300.0
		SetActorLocation(NewLocation);
	}
}

