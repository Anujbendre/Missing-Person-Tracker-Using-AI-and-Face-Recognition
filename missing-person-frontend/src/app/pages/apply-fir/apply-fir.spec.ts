import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ApplyFir } from './apply-fir';

describe('ApplyFir', () => {
  let component: ApplyFir;
  let fixture: ComponentFixture<ApplyFir>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ApplyFir],
    }).compileComponents();

    fixture = TestBed.createComponent(ApplyFir);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
