import { Component, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-cctv',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './cctv.html',
  styleUrls: ['./cctv.css']
})
export class CctvComponent implements AfterViewInit {

  @ViewChild('video') video!: ElementRef<HTMLVideoElement>;

  isCameraOn = false;
  stream: MediaStream | null = null;
  intervalId: any;

  constructor(private http: HttpClient) {}

  ngAfterViewInit() {
    // optional auto start
    // this.startCamera();
  }

  // ================= START CAMERA =================
  startCamera() {
  this.isCameraOn = true;

  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      this.stream = stream;
      this.video.nativeElement.srcObject = stream;

      // 🔥 AUTO CAPTURE EVERY 3 SEC
      this.intervalId = setInterval(() => {
        this.captureAndSave();
      }, 3000);

    })
    .catch(err => {
      console.error("Camera Error:", err);
    });
}



  // ================= CAPTURE + SEND =================
  captureAndSave() {
  const video = this.video.nativeElement;

  if (!video.videoWidth) return;

  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const ctx = canvas.getContext('2d');
  ctx?.drawImage(video, 0, 0);

  const image = canvas.toDataURL('image/jpeg');

  console.log("Sending image..."); // 🔥 DEBUG

  this.http.post('http://127.0.0.1:8000/api/save-frame', {
    image: image
  }).subscribe(res => {
    console.log("Saved:", res);
  }, err => {
    console.error("Error saving:", err);
  });
}

stopCamera() {
  this.isCameraOn = false;

  if (this.stream) {
    this.stream.getTracks().forEach((track: any) => track.stop());
  }

  // 🔥 STOP AUTO CAPTURE
  if (this.intervalId) {
    clearInterval(this.intervalId);
  }
}
}