import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PoliceLogin } from './police-login';

describe('PoliceLogin', () => {
  let component: PoliceLogin;
  let fixture: ComponentFixture<PoliceLogin>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PoliceLogin],
    }).compileComponents();

    fixture = TestBed.createComponent(PoliceLogin);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
