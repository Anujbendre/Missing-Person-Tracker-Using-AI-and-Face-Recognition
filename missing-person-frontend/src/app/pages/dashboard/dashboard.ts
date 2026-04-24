import {
  Component,
  OnInit,
  OnDestroy,
  AfterViewInit,
  ChangeDetectorRef,
  HostListener
} from '@angular/core';

import { CommonModule } from '@angular/common';
import { TranslateService, TranslateModule } from '@ngx-translate/core';
import { RouterModule } from '@angular/router';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';

import { SignupComponent } from '../signup/signup';
import { LoginComponent } from '../login/login';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, TranslateModule, RouterModule, MatDialogModule],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css']
})
export class Dashboard implements OnInit, OnDestroy, AfterViewInit {

  // ================= IMAGES =================
  images: string[] = [
    '/assets/p1.png',
    '/assets/p2.png',
    '/assets/p3.png',
    '/assets/p4.png'
  ];

  currentIndex = 0;
  activeDropdown: string | null = null;
  private intervalId: any;
  isScrolled = false;

  constructor(
    private dialog: MatDialog,
    private translate: TranslateService,
    private cdr: ChangeDetectorRef
  ) {
    this.setupTranslations();
  }

  // ================= TRANSLATION SETUP =================
  setupTranslations() {
    this.translate.addLangs(['en', 'hi', 'mr']);
    this.translate.setDefaultLang('en');

    this.translate.setTranslation('en', {
      TITLE: 'PUNE CITY POLICE',
      ABOUT: 'About Us',
      CITIZEN: 'Citizen Corner',
      POLICE: 'Police Corner',
      REPORT: 'Report Us',
      SEARCH: 'Search: Missing Person / FIR / Complaint'
    });

    this.translate.setTranslation('hi', {
      TITLE: 'पुणे शहर पुलिस',
      ABOUT: 'हमारे बारे में',
      CITIZEN: 'नागरिक कोना',
      POLICE: 'पुलिस कोना',
      REPORT: 'रिपोर्ट करें',
      SEARCH: 'खोजें: लापता व्यक्ति / एफआईआर / शिकायत'
    });

    this.translate.setTranslation('mr', {
      TITLE: 'पुणे शहर पोलीस',
      ABOUT: 'आमच्याबद्दल',
      CITIZEN: 'नागरिक विभाग',
      POLICE: 'पोलीस विभाग',
      REPORT: 'तक्रार नोंदवा',
      SEARCH: 'शोधा: हरवलेली व्यक्ती / FIR / तक्रार'
    });

    this.translate.use('en');
  }

  // ================= POPUPS =================
  openSignup() {
    this.dialog.open(SignupComponent, { width: '420px' });
  }

  openLogin() {
    this.dialog.open(LoginComponent, { width: '400px' });
  }

  // ================= DROPDOWN =================
  toggleDropdown(menu: string) {
    this.activeDropdown = this.activeDropdown === menu ? null : menu;
  }

  closeDropdown() {
    this.activeDropdown = null;
  }

  // ================= SLIDER =================
  ngOnInit() {
    this.startSlider();
  }

  ngAfterViewInit() {
    // ✅ FIX ExpressionChangedAfterItHasBeenCheckedError
    setTimeout(() => {
      this.cdr.detectChanges();
    });
  }

  startSlider() {
    this.intervalId = setInterval(() => {
      this.currentIndex = (this.currentIndex + 1) % this.images.length;
    }, 2000);
  }

  ngOnDestroy() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }

  // ================= LANGUAGE =================
  changeLang(lang: string) {
    this.translate.use(lang);
  }

  // ================= SCROLL DETECTION =================
  @HostListener('window:scroll', [])
  onWindowScroll() {
    const scrollPosition = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
    this.isScrolled = scrollPosition > 50;
  }

  // Close dropdown when clicking outside
  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event) {
    const target = event.target as HTMLElement;
    if (!target.closest('.dropdown')) {
      this.closeDropdown();
    }
  }
}