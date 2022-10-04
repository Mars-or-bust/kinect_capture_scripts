// Create and initialze the MediaCapture object.
public async void InitMediaCapture()
{
    _mediaCapture = null;
    _mediaCapture = new Windows.Media.Capture.MediaCapture();

    // Set the MediaCapture to a variable in App.xaml.cs to handle suspension.
    (App.Current as App).MediaCapture = _mediaCapture;

    await _mediaCapture.InitializeAsync(_captureInitSettings);

    CreateProfile();
}

int main(int argc, char** argv)
{
    mediaCapture.RecordLimitationExceeded += MediaCapture_RecordLimitationExceeded;

    var localFolder = Windows.Storage.ApplicationData.Current.LocalFolder;
    StorageFile file = await localFolder.CreateFileAsync("audio.mp3", CreationCollisionOption.GenerateUniqueName);
    _mediaRecording = await mediaCapture.PrepareLowLagRecordToStorageFileAsync(
            MediaEncodingProfile.CreateMp3(AudioEncodingQuality.High), file);
    await _mediaRecording.StartAsync();
}