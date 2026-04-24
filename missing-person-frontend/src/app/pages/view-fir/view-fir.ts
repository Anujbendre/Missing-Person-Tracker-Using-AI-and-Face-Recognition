import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef } from '@angular/core';
import jsPDF from 'jspdf';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-view-fir',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './view-fir.html',
  styleUrls: ['./view-fir.css']
})
export class ViewFirComponent implements OnInit {

  firList: any[] = [];
  filteredList: any[] = [];
  searchText: string = '';

  // ✅ FIX: inject HttpClient
  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}


  ngOnInit(): void {
    this.loadFIRs();
  }

loadFIRs() {
  this.http.get<{ data: any[] }>('http://127.0.0.1:8000/api/fir')
    .subscribe((res) => {

      this.firList = res.data;

      // ✅ create new reference
      this.filteredList = [...this.firList];

      // 🔥 FORCE CHANGE DETECTION
      this.cdr.detectChanges();

      console.log("FINAL DATA:", this.filteredList);
    });
}

  // ✅ SEARCH FUNCTION
onSearch() {
  if (!this.searchText) {
    this.filteredList = [...this.firList];
  } else {
    this.filteredList = this.firList.filter(f =>
      f.location.toLowerCase().includes(this.searchText.toLowerCase())
    );
  }

  this.cdr.detectChanges(); // 🔥 update UI
}

downloadPDF(fir: any) {
  const doc = new jsPDF();
  let y = 10;

  // 🔥 HEADER
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(14);
  doc.text('FORM - IF1 (Integrated Form)', 55, y);
  y += 8;

  doc.setFontSize(16);
  doc.text('FIRST INFORMATION REPORT', 40, y);
  y += 6;

  doc.setFontSize(10);
  doc.text('(Under Section 154 Cr.P.C)', 60, y);
  y += 10;

  // 🔲 OUTER BORDER
  doc.setLineWidth(0.5);
  doc.rect(5, 5, 200, 287);

  // 🔹 SECTION 1
  doc.setFontSize(11);
  doc.setFont('helvetica', 'normal');

  doc.text(`1. FIR No: ${fir.fir_id}`, 10, y);
  doc.text(`Date: ${fir.date || new Date().toLocaleDateString()}`, 120, y);
  y += 8;

  // 🔹 SECTION 2
  doc.text(`2. Act & Sections: ${fir.incident_type || 'N/A'}`, 10, y);
  y += 8;

  // 🔹 SECTION 3
  doc.text(`3. Occurrence of Offence:`, 10, y);
  y += 6;

  doc.text(
    `Date: ${fir.date || 'N/A'}   Time: ${fir.time || 'N/A'}`,
    15,
    y
  );
  y += 6;

  doc.text(
    `Information received at P.S: Pune Police Station`,
    15,
    y
  );
  y += 10;

  // 🔹 SECTION 4
  doc.text(`4. Type of Information: Written`, 10, y);
  y += 10;

  // 🔹 SECTION 5
  doc.text(`5. Place of Occurrence:`, 10, y);
  y += 6;

  doc.text(`Address: ${fir.location || 'N/A'}`, 15, y);
  y += 10;

  // 🔹 SECTION 6
  doc.text(`6. Complainant / Informant:`, 10, y);
  y += 6;

  doc.text(`(a) Name: ${fir.full_name || 'N/A'}`, 15, y);
  y += 6;

  doc.text(`(b) Email: ${fir.email || 'N/A'}`, 15, y);
  y += 6;

  doc.text(`(c) Phone: ${fir.phone || 'N/A'}`, 15, y);
  y += 10;

  // 🔹 SECTION 7
  doc.text(
    `7. Accused Details: ${fir.accused || 'Unknown / Not Provided'}`,
    10,
    y
  );
  y += 10;

  // 🔹 SECTION 8
  doc.text(
    `8. Reason for delay (if any): ${fir.delay_reason || 'No delay in reporting'}`,
    10,
    y
  );
  y += 10;

  // 🔹 SECTION 9
  doc.text(
    `9. Property involved: ${fir.property || 'Not specified'}`,
    10,
    y
  );
  y += 10;

  // 🔹 SECTION 10
  doc.text(
    `10. Total Value: ${fir.property_value || 'N/A'}`,
    10,
    y
  );
  y += 10;

  // 🔹 SECTION 12 (FIR CONTENT)
  doc.text(`12. FIR Contents:`, 10, y);
  y += 6;

  const content = doc.splitTextToSize(
    `Incident: ${fir.incident_type || 'N/A'} reported at ${fir.location || 'N/A'}.`,
    180
  );

  doc.text(content, 15, y);
  y += content.length * 6 + 10;

  // 🔹 SECTION 13
  doc.text(`13. Action Taken: Investigation started.`, 10, y);
  y += 15;

  // 🔹 SIGNATURE AREA
  doc.text(`Signature of Officer`, 10, y);
  doc.text(`Signature of Complainant`, 120, y);

  // 🔥 SAVE PDF
  doc.save(`FIR_${fir.fir_id}.pdf`);
}


selectedFIR: any = null;   // 🔥 IMPORTANT

viewFIR(fir: any) {
  console.log("Clicked FIR:", fir);  // 👈 debug
  this.selectedFIR = fir;
}

closeModal() {
  this.selectedFIR = null;
}
}

