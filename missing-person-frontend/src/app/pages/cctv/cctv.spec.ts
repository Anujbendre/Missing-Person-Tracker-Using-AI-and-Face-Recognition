import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Cctv } from './cctv';

describe('Cctv', () => {
  let component: Cctv;
  let fixture: ComponentFixture<Cctv>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Cctv],
    }).compileComponents();

    fixture = TestBed.createComponent(Cctv);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
