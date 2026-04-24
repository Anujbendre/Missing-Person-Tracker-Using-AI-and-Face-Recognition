import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PoliceCases } from './police-cases';

describe('PoliceCases', () => {
  let component: PoliceCases;
  let fixture: ComponentFixture<PoliceCases>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PoliceCases],
    }).compileComponents();

    fixture = TestBed.createComponent(PoliceCases);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
