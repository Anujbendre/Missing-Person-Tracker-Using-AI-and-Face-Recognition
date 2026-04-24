import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { ReportMissingComponent } from '../report-missing/report-missing';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-citizen-dashboard',
  standalone: true,
  imports: [CommonModule, MatDialogModule, RouterModule],
  templateUrl: './citizen-dashboard.html',
  styleUrls: ['./citizen-dashboard.css']
})
export class CitizenDashboardComponent {

  activeSection: string = '';

  constructor(
    private authService: AuthService,
    private dialog: MatDialog
  ) {}

  // ✅ OPEN POPUP
  openReportPopup() {
    this.dialog.open(ReportMissingComponent, {
      width: '600px',   // 👈 BIG POPUP
      height: 'auto',
      panelClass: 'custom-dialog'
    });
  }

  // ✅ SIDEBAR CLICK
  setSection(section: string) {
    this.activeSection = section;

    if (section === 'report') {
      this.openReportPopup(); // 🔥 OPEN POPUP INSTEAD OF ROUTE
    }
  }
}