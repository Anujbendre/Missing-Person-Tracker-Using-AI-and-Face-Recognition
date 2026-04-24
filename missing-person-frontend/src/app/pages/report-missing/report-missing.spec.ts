import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReportMissing } from './report-missing';

describe('ReportMissing', () => {
  let component: ReportMissing;
  let fixture: ComponentFixture<ReportMissing>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReportMissing],
    }).compileComponents();

    fixture = TestBed.createComponent(ReportMissing);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
