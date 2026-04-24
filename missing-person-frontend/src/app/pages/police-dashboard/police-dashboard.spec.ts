import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PoliceDashboard } from './police-dashboard';

describe('PoliceDashboard', () => {
  let component: PoliceDashboard;
  let fixture: ComponentFixture<PoliceDashboard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PoliceDashboard],
    }).compileComponents();

    fixture = TestBed.createComponent(PoliceDashboard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
