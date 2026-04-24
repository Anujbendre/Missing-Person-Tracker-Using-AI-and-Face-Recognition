import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MyCases } from './my-cases';

describe('MyCases', () => {
  let component: MyCases;
  let fixture: ComponentFixture<MyCases>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MyCases],
    }).compileComponents();

    fixture = TestBed.createComponent(MyCases);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
