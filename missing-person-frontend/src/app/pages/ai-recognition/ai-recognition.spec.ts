import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AiRecognition } from './ai-recognition';

describe('AiRecognition', () => {
  let component: AiRecognition;
  let fixture: ComponentFixture<AiRecognition>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AiRecognition],
    }).compileComponents();

    fixture = TestBed.createComponent(AiRecognition);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
