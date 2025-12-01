import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CreateEspaciosComponent } from './create-espacios.component';

describe('CreateEspaciosComponent', () => {
  let component: CreateEspaciosComponent;
  let fixture: ComponentFixture<CreateEspaciosComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreateEspaciosComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CreateEspaciosComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
