import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CertificadoCreateComponent } from './certificado-create.component';

describe('CertificadoCreateComponent', () => {
  let component: CertificadoCreateComponent;
  let fixture: ComponentFixture<CertificadoCreateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CertificadoCreateComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CertificadoCreateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
