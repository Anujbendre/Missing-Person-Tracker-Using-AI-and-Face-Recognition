import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-faqs',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './faqs.html',
  styleUrls: ['./faqs.css']
})
export class FAQs {

  activeIndex: number | null = null;

  faqs = [
    {
      question: 'How to report a missing person?',
      answer: 'Go to Citizen Corner → Report Missing Person and fill the form.'
    },
    {
      question: 'Is this system free?',
      answer: 'Yes, this system is completely free for public use.'
    },
    {
      question: 'How does AI identify a person?',
      answer: 'It uses facial recognition to match images from database.'
    },
    {
      question: 'Can police access more features?',
      answer: 'Yes, police and admin have secure login with advanced tools.'
    }
  ];

  toggleFAQ(index: number) {
    this.activeIndex = this.activeIndex === index ? null : index;
  }
}