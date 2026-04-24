import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewMissing } from './view-missing';

describe('ViewMissing', () => {
  let component: ViewMissing;
  let fixture: ComponentFixture<ViewMissing>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ViewMissing],
    }).compileComponents();

    fixture = TestBed.createComponent(ViewMissing);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
