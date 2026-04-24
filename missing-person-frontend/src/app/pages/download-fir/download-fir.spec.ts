import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DownloadFir } from './download-fir';

describe('DownloadFir', () => {
  let component: DownloadFir;
  let fixture: ComponentFixture<DownloadFir>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DownloadFir],
    }).compileComponents();

    fixture = TestBed.createComponent(DownloadFir);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
