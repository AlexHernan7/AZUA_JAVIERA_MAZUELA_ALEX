import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JuntaCreateComponent } from './junta-create.component';

describe('JuntaCreateComponent', () => {
  let component: JuntaCreateComponent;
  let fixture: ComponentFixture<JuntaCreateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JuntaCreateComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(JuntaCreateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
