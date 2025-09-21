import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DirectivaRegisterComponent } from './directiva-register.component';

describe('DirectivaRegisterComponent', () => {
  let component: DirectivaRegisterComponent;
  let fixture: ComponentFixture<DirectivaRegisterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DirectivaRegisterComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(DirectivaRegisterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
