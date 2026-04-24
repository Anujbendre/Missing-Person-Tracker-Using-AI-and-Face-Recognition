import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PoliceSignup } from './police-signup';

describe('PoliceSignup', () => {
  let component: PoliceSignup;
  let fixture: ComponentFixture<PoliceSignup>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PoliceSignup],
    }).compileComponents();

    fixture = TestBed.createComponent(PoliceSignup);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
