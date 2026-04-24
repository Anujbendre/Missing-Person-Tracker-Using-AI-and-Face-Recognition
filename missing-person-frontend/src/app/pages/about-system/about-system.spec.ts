import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AboutSystem } from './about-system';

describe('AboutSystem', () => {
  let component: AboutSystem;
  let fixture: ComponentFixture<AboutSystem>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AboutSystem],
    }).compileComponents();

    fixture = TestBed.createComponent(AboutSystem);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
