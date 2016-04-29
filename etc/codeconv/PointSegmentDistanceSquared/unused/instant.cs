class conv {
private double PointSegmentDistanceSquared(double px, double py, double p1x, double p1y, double p2x, double p2y, ref double t, ref double qx, ref double qy)
{
	const double kMinSegmentLenSquared = 0.00000001; // adjust to suit.  If you use float, you'll probably want something like 0.000001f
	const double kEpsilon = 1.0E-14; // adjust to suit.  If you use floats, you'll probably want something like 1E-7f
	double dx = p2x - p1x;
	double dy = p2y - p1y;
	double dp1x = px - p1x;
	double dp1y = py - p1y;
//JAVA TO C# CONVERTER WARNING: The original Java variable was marked 'final':
//ORIGINAL LINE: final double segLenSquared = (dx * dx) + (dy * dy);
	double segLenSquared = (dx * dx) + (dy * dy);
	if (segLenSquared >= -kMinSegmentLenSquared && segLenSquared <= kMinSegmentLenSquared)
	{
		// segment is a point.
		qx.argValue = p1x;
		qy.argValue = p1y;
		t.argValue = 0.0;
		return ((dp1x * dp1x) + (dp1y * dp1y));
	}
	else
	{
		// Project a line from p to the segment [p1,p2].  By considering the line
		// extending the segment, parameterized as p1 + (t * (p2 - p1)),
		// we find projection of point p onto the line. 
		// It falls where t = [(p - p1) . (p2 - p1)] / |p2 - p1|^2
		t.argValue = ((dp1x * dx) + (dp1y * dy)) / segLenSquared;
		if (t.argValue < kEpsilon)
		{
			// intersects at or to the "left" of first segment vertex (p1x, p1y).  If t is approximately 0.0, then
			// intersection is at p1.  If t is less than that, then there is no intersection (i.e. p is not within
			// the 'bounds' of the segment)
			if (t.argValue > -kEpsilon)
			{
				// intersects at 1st segment vertex
				t.argValue = 0.0;
			}
			// set our 'intersection' point to p1.
			qx.argValue = p1x;
			qy.argValue = p1y;
			// Note: If you wanted the ACTUAL intersection point of where the projected lines would intersect if
			// we were doing PointLineDistanceSquared, then qx would be (p1x + (t * dx)) and qy would be (p1y + (t * dy)).
		}
		else if (t.argValue > (1.0 - kEpsilon))
		{
			// intersects at or to the "right" of second segment vertex (p2x, p2y).  If t is approximately 1.0, then
			// intersection is at p2.  If t is greater than that, then there is no intersection (i.e. p is not within
			// the 'bounds' of the segment)
			if (t.argValue < (1.0 + kEpsilon))
			{
				// intersects at 2nd segment vertex
				t.argValue = 1.0;
			}
			// set our 'intersection' point to p2.
			qx.argValue = p2x;
			qy.argValue = p2y;
			// Note: If you wanted the ACTUAL intersection point of where the projected lines would intersect if
			// we were doing PointLineDistanceSquared, then qx would be (p1x + (t * dx)) and qy would be (p1y + (t * dy)).
		}
		else
		{
			// The projection of the point to the point on the segment that is perpendicular succeeded and the point
			// is 'within' the bounds of the segment.  Set the intersection point as that projected point.
			qx.argValue = p1x + (t.argValue * dx);
			qy.argValue = p1y + (t.argValue * dy);
		}
		// return the squared distance from p to the intersection point.  Note that we return the squared distance
		// as an optimization because many times you just need to compare relative distances and the squared values
		// works fine for that.  If you want the ACTUAL distance, just take the square root of this value.
		double dpqx = px - qx.argValue;
		double dpqy = py - qy.argValue;
		return ((dpqx * dpqx) + (dpqy * dpqy));
	}
}

}
