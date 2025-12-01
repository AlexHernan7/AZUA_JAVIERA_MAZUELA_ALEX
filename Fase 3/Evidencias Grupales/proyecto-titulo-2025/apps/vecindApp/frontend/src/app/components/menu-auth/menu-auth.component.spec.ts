import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MenuAuthComponent } from './menu-auth.component';

describe('MenuAuthComponent', () => {
  let component: MenuAuthComponent;
  let fixture: ComponentFixture<MenuAuthComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MenuAuthComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(MenuAuthComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
