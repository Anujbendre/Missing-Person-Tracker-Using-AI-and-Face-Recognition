import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewFir } from './view-fir';

describe('ViewFir', () => {
  let component: ViewFir;
  let fixture: ComponentFixture<ViewFir>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ViewFir],
    }).compileComponents();

    fixture = TestBed.createComponent(ViewFir);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
