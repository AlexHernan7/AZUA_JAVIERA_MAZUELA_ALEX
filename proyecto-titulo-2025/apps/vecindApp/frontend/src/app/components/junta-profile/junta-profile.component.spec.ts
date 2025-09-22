import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JuntaProfileComponent } from './junta-profile.component';

describe('JuntaProfileComponent', () => {
  let component: JuntaProfileComponent;
  let fixture: ComponentFixture<JuntaProfileComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JuntaProfileComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(JuntaProfileComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
